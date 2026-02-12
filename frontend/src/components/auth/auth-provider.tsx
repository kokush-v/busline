"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useQuery } from "@tanstack/react-query";
import type {
  AuthResponse,
  ConfirmSignUpRequest,
  LoginRequest,
  SignUpRequest,
  TokenResponse,
  UserRead,
} from "@/generated/api/model";
import {
  getProfile,
  postConfirmSignUp,
  postLogin,
  postRefreshTokens,
  postSignOut,
  postSignUp,
} from "@/generated/api/endpoints/authentication/authentication";
import type { StoredAuth } from "@/types/auth";
import {
  clearStoredAuth,
  readStoredAuth,
  writeStoredAuth,
} from "@/utils/auth";
import { PageSkeleton } from "@/components/page-skeleton";

type AuthContextValue = {
  user: UserRead | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (
    payload: LoginRequest & { rememberMe?: boolean },
  ) => Promise<TokenResponse>;
  register: (payload: SignUpRequest) => Promise<AuthResponse>;
  verify: (payload: ConfirmSignUpRequest) => Promise<AuthResponse>;
  refresh: () => Promise<TokenResponse | null>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const buildSession = (
  tokens: TokenResponse,
  fallbackUser?: UserRead | null,
) => {
  const accessToken = tokens.access_token;
  const refreshToken = tokens.refresh_token ?? null;
  const expiresAt = tokens.expires_in
    ? Date.now() + tokens.expires_in * 1000
    : undefined;
  return { accessToken, refreshToken, expiresAt, user: fallbackUser ?? null };
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // Use Query for initial auth state with loading indicator
  const { data: initialAuth, isLoading } = useQuery({
    queryKey: ["auth", "session"],
    queryFn: async (): Promise<StoredAuth | null> => {
      try {
        const stored = readStoredAuth();
        if (!stored?.accessToken) return null;

        if (
          stored.expiresAt &&
          stored.expiresAt <= Date.now() &&
          stored.refreshToken
        ) {
          const refreshed = await postRefreshTokens({
            refresh_token: stored.refreshToken,
          });
          const profile = await getProfile();

          const updatedAuth: StoredAuth = {
            user: profile,
            accessToken: refreshed.access_token,
            refreshToken: refreshed.refresh_token ?? null,
            expiresAt: refreshed.expires_in
              ? Date.now() + refreshed.expires_in * 1000
              : undefined,
            rememberMe: stored.rememberMe,
          };

          writeStoredAuth(updatedAuth);
          return updatedAuth;
        }

        const profile = await getProfile();
        const updatedAuth: StoredAuth = {
          ...stored,
          user: profile,
        };
        writeStoredAuth(updatedAuth);

        return updatedAuth;
      } catch {
        clearStoredAuth();
        return null;
      }
    },
    staleTime: Infinity,
    gcTime: Infinity,
  });

  const [user, setUser] = useState<UserRead | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const refreshFnRef = useRef<() => Promise<TokenResponse | null>>(
    async () => null,
  );
  const rememberMeRef = useRef(false);

  // Update states when initialAuth is loaded
  useEffect(() => {
    if (initialAuth) {
      setUser(initialAuth.user ?? null);
      setAccessToken(initialAuth.accessToken ?? null);
      setRefreshToken(initialAuth.refreshToken ?? null);
      rememberMeRef.current = initialAuth.rememberMe ?? false;
    }
  }, [initialAuth]);

  const clearRefreshTimer = useCallback(() => {
    if (refreshTimer.current) {
      clearTimeout(refreshTimer.current);
      refreshTimer.current = null;
    }
  }, []);

  const scheduleRefresh = useCallback(
    (session: { expiresAt?: number; refreshToken: string | null }) => {
      if (!session.expiresAt || !session.refreshToken) return;
      const msBeforeExpiry = session.expiresAt - Date.now();
      const msUntilRefresh = Math.max(msBeforeExpiry - 60_000, 5_000);
      clearRefreshTimer();
      refreshTimer.current = setTimeout(() => {
        void refreshFnRef.current();
      }, msUntilRefresh);
    },
    [clearRefreshTimer],
  );

  const applyAuth = useCallback(
    (
      tokens: TokenResponse,
      rememberMe: boolean,
      fallbackUser?: UserRead | null,
    ) => {
      const session = buildSession(tokens, fallbackUser);
      setAccessToken(session.accessToken);
      setRefreshToken(session.refreshToken ?? null);
      setUser(session.user ?? null);
      writeStoredAuth({
        user: session.user ?? null,
        accessToken: session.accessToken,
        refreshToken: session.refreshToken ?? null,
        expiresAt: session.expiresAt,
        rememberMe,
      });
      scheduleRefresh(session);
      return session;
    },
    [scheduleRefresh],
  );

  const fetchAndStoreProfile = useCallback(
    async (
      token: string,
      refreshValue: string | null,
      rememberMe: boolean,
      expiresAt?: number,
    ) => {
      try {
        const profile = await getProfile();
        setUser(profile);
        setAccessToken(token);
        setRefreshToken(refreshValue ?? null);
        writeStoredAuth({
          user: profile,
          accessToken: token,
          refreshToken: refreshValue ?? null,
          expiresAt,
          rememberMe,
        });
        scheduleRefresh({ expiresAt, refreshToken: refreshValue ?? null });
      } catch {
        // ignore profile fetch errors
      }
    },
    [scheduleRefresh],
  );

  const handleLogin = useCallback(
    async ({
      email,
      password,
      rememberMe,
    }: LoginRequest & { rememberMe?: boolean }) => {
      const tokens = await postLogin({ email, password });
      const session = applyAuth(tokens, Boolean(rememberMe));
      rememberMeRef.current = Boolean(rememberMe);
      await fetchAndStoreProfile(
        session.accessToken,
        session.refreshToken ?? null,
        Boolean(rememberMe),
        session.expiresAt,
      );
      return tokens;
    },
    [applyAuth, fetchAndStoreProfile],
  );

  const handleRegister = useCallback(async (payload: SignUpRequest) => {
    const response = await postSignUp(payload);
    return response;
  }, []);

  const handleVerify = useCallback(async (payload: ConfirmSignUpRequest) => {
    return postConfirmSignUp(payload);
  }, []);

  const handleRefresh = useCallback(async () => {
    const stored = readStoredAuth();
    const tokenToUse = stored?.refreshToken ?? refreshToken;
    if (!tokenToUse) return null;
    const rememberMe = stored?.rememberMe ?? rememberMeRef.current;
    const refreshed = await postRefreshTokens({ refresh_token: tokenToUse });
    const session = applyAuth(refreshed, rememberMe, stored?.user ?? user);
    await fetchAndStoreProfile(
      session.accessToken,
      session.refreshToken,
      rememberMe,
      session.expiresAt,
    );
    return refreshed;
  }, [applyAuth, fetchAndStoreProfile, refreshToken, user]);

  useEffect(() => {
    refreshFnRef.current = handleRefresh;
  }, [handleRefresh]);

  const handleLogout = useCallback(async () => {
    try {
      if (accessToken) {
        await postSignOut();
      }
    } finally {
      clearRefreshTimer();
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      clearStoredAuth();
    }
  }, [accessToken, clearRefreshTimer]);

  // Schedule refresh on mount if we have initial auth
  useEffect(() => {
    if (initialAuth) {
      scheduleRefresh({
        expiresAt: initialAuth.expiresAt,
        refreshToken: initialAuth.refreshToken ?? null,
      });
    }
    return () => clearRefreshTimer();
  }, [initialAuth, scheduleRefresh, clearRefreshTimer]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      accessToken,
      refreshToken,
      isAuthenticated: Boolean(accessToken),
      login: handleLogin,
      register: handleRegister,
      verify: handleVerify,
      refresh: handleRefresh,
      logout: handleLogout,
    }),
    [
      user,
      accessToken,
      refreshToken,
      handleLogin,
      handleRegister,
      handleVerify,
      handleRefresh,
      handleLogout,
    ],
  );

  if (isLoading) {
    return <PageSkeleton />;
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
