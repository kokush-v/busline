import type { StoredAuth } from "@/types/auth";
import { isBrowser } from "@/utils/common";

const STORAGE_KEY = "busLine.auth";
const ACCESS_TOKEN_KEY = "token";

export const readStoredAuth = (): StoredAuth | null => {
  if (!isBrowser()) return null;
  const raw =
    localStorage.getItem(STORAGE_KEY) ?? sessionStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredAuth;
  } catch {
    return null;
  }
};

export const writeStoredAuth = (auth: StoredAuth): void => {
  if (!isBrowser()) return;
  const storage = auth.rememberMe ? localStorage : sessionStorage;
  const otherStorage = auth.rememberMe ? sessionStorage : localStorage;
  storage.setItem(STORAGE_KEY, JSON.stringify(auth));
  storage.setItem(ACCESS_TOKEN_KEY, auth.accessToken);
  otherStorage.removeItem(STORAGE_KEY);
  otherStorage.removeItem(ACCESS_TOKEN_KEY);
};

export const persistAccessToken = (
  token: string | null,
  rememberMe: boolean,
): void => {
  if (!isBrowser()) return;
  const storage = rememberMe ? localStorage : sessionStorage;
  const otherStorage = rememberMe ? sessionStorage : localStorage;
  if (token) {
    storage.setItem(ACCESS_TOKEN_KEY, token);
  } else {
    storage.removeItem(ACCESS_TOKEN_KEY);
  }
  otherStorage.removeItem(ACCESS_TOKEN_KEY);
};

export const clearStoredAuth = (): void => {
  if (!isBrowser()) return;
  localStorage.removeItem(STORAGE_KEY);
  sessionStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
};
