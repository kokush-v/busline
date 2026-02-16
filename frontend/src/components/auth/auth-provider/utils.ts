import type { TokenResponse, UserRead } from "@/generated/api/model";
import type { StoredAuth } from "@/types/auth";
import { writeStoredAuth } from "@/utils/auth";
import {
  getProfile,
  postRefreshTokens,
} from "@/generated/api/endpoints/authentication/authentication";
import type { Session } from "./types";

export const buildSession = (
  tokens: TokenResponse,
  fallbackUser?: UserRead | null,
): Session => {
  const accessToken = tokens.access_token;
  const refreshToken = tokens.refresh_token ?? null;
  const expiresAt = tokens.expires_in
    ? Date.now() + tokens.expires_in * 1000
    : undefined;
  return { accessToken, refreshToken, expiresAt, user: fallbackUser ?? null };
};

export const refreshTokensAndFetchProfile = async (
  refreshToken: string,
  rememberMe: boolean,
): Promise<StoredAuth> => {
  const refreshed = await postRefreshTokens({ refresh_token: refreshToken });

  const refreshedAuth: StoredAuth = {
    user: null,
    accessToken: refreshed.access_token,
    refreshToken: refreshed.refresh_token ?? null,
    expiresAt: refreshed.expires_in
      ? Date.now() + refreshed.expires_in * 1000
      : undefined,
    rememberMe,
  };
  writeStoredAuth(refreshedAuth);

  const profile = await getProfile();
  const updatedAuth: StoredAuth = {
    ...refreshedAuth,
    user: profile,
  };
  writeStoredAuth(updatedAuth);

  return updatedAuth;
};
