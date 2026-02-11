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
  persistAccessToken,
  readStoredAuth,
  writeStoredAuth,
} from "@/utils/auth";

type AuthContextValue = {
  user: UserRead | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
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
  const [user, setUser] = useState<UserRead | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const refreshFnRef = useRef<() => Promise<TokenResponse | null>>(
    async () => null,
  );
  const rememberMeRef = useRef(false);

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
      persistAccessToken(session.accessToken, rememberMe);
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
        persistAccessToken(token, rememberMe);
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
      setIsLoading(true);
      try {
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
      } finally {
        setIsLoading(false);
      }
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
    setIsLoading(true);
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
      setIsLoading(false);
    }
  }, [accessToken, clearRefreshTimer]);

  const bootstrap = useCallback(async () => {
    setIsLoading(true);
    try {
      const stored = readStoredAuth();
      if (!stored?.accessToken) return;
      rememberMeRef.current = stored.rememberMe;
      if (
        stored.expiresAt &&
        stored.expiresAt <= Date.now() &&
        stored.refreshToken
      ) {
        const refreshed = await postRefreshTokens({
          refresh_token: stored.refreshToken,
        });
        const session = applyAuth(refreshed, stored.rememberMe, stored.user);
        await fetchAndStoreProfile(
          session.accessToken,
          session.refreshToken,
          stored.rememberMe,
          session.expiresAt,
        );
        return;
      }
      await fetchAndStoreProfile(
        stored.accessToken,
        stored.refreshToken ?? null,
        stored.rememberMe,
        stored.expiresAt,
      );
      setAccessToken(stored.accessToken);
      setRefreshToken(stored.refreshToken ?? null);
      setUser(stored.user ?? null);
      scheduleRefresh({
        expiresAt: stored.expiresAt,
        refreshToken: stored.refreshToken ?? null,
      });
    } catch {
      clearStoredAuth();
      setUser(null);
      setAccessToken(null);
      setRefreshToken(null);
      persistAccessToken(null, true);
    } finally {
      setIsLoading(false);
    }
  }, [applyAuth, fetchAndStoreProfile, scheduleRefresh]);

  useEffect(() => {
    void bootstrap();
    return () => clearRefreshTimer();
  }, [bootstrap, clearRefreshTimer]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      accessToken,
      refreshToken,
      isAuthenticated: Boolean(accessToken),
      isLoading,
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
      isLoading,
      handleLogin,
      handleRegister,
      handleVerify,
      handleRefresh,
      handleLogout,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
