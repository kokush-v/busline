export type StoredAuth = {
  user: import("@/generated/api/model").UserRead | null;
  accessToken: string;
  refreshToken: string | null;
  expiresAt?: number;
  rememberMe: boolean;
};
