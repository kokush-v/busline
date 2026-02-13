import { UserRead } from "@/generated/api/model";

export type StoredAuth = {
  user: UserRead | null;
  accessToken: string;
  refreshToken: string | null;
  expiresAt?: number;
  rememberMe: boolean;
};
