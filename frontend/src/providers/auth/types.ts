import type {
  AuthResponse,
  ConfirmSignUpRequest,
  LoginRequest,
  SignUpRequest,
  TokenResponse,
  UserRead,
} from "@/generated/api/model";

export type AuthContextValue = {
  user: UserRead | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  authError: Error | null;
  login: (
    payload: LoginRequest & { rememberMe?: boolean },
  ) => Promise<TokenResponse>;
  register: (payload: SignUpRequest) => Promise<AuthResponse>;
  verify: (payload: ConfirmSignUpRequest) => Promise<AuthResponse>;
  refresh: () => Promise<TokenResponse | null>;
  logout: () => Promise<void>;
};

export type Session = {
  accessToken: string;
  refreshToken: string | null;
  expiresAt?: number;
  user: UserRead | null;
};
