"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import type {
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
import { clearStoredAuth, readStoredAuth, writeStoredAuth } from "@/utils/auth";
import { PageSkeleton } from "@/components/page-skeleton";
import { AuthContext } from "./context";
import { buildSession, refreshTokensAndFetchProfile } from "./utils";
import type { AuthContextValue } from "./types";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: initialAuth, isLoading } = useQuery({
    queryKey: ["auth", "session"],
    queryFn: async (): Promise<StoredAuth | null> => {
      const stored = readStoredAuth();
      if (!stored?.accessToken) return null;

      const tryRefresh = async (): Promise<StoredAuth | null> => {
        if (!stored.refreshToken) {
          clearStoredAuth();
          return null;
        }
        try {
          return await refreshTokensAndFetchProfile(
            stored.refreshToken,
            stored.rememberMe ?? false,
          );
        } catch {
          clearStoredAuth();
          return null;
        }
      };

      const isExpired = stored.expiresAt && stored.expiresAt <= Date.now();
      if (isExpired) {
        return await tryRefresh();
      }

      try {
        const profile = await getProfile();
        const updatedAuth: StoredAuth = {
          ...stored,
          user: profile,
        };
        writeStoredAuth(updatedAuth);
        return updatedAuth;
      } catch {
        if (stored.rememberMe) {
          return await tryRefresh();
        }
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

  const applyAuthWithProfile = useCallback(
    async (tokens: TokenResponse, rememberMe: boolean) => {
      const session = applyAuth(tokens, rememberMe);

      try {
        const profile = await getProfile();
        setUser(profile);
        const stored = readStoredAuth();
        if (stored) {
          writeStoredAuth({ ...stored, user: profile });
        }
      } catch {}

      return session;
    },
    [applyAuth],
  );

  const handleLogin = useCallback(
    async ({
      email,
      password,
      rememberMe,
    }: LoginRequest & { rememberMe?: boolean }) => {
      const tokens = await postLogin({ email, password });
      rememberMeRef.current = Boolean(rememberMe);
      await applyAuthWithProfile(tokens, Boolean(rememberMe));
      return tokens;
    },
    [applyAuthWithProfile],
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
    await applyAuthWithProfile(refreshed, rememberMe);
    return refreshed;
  }, [applyAuthWithProfile, refreshToken]);

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

export { useAuth } from "./use-auth";
export type { AuthContextValue } from "./types";
