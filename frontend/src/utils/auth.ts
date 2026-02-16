import type { StoredAuth } from "@/types/auth";
import { isBrowser } from "@/utils/common";

const STORAGE_KEY = "busLine.auth";

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

export const getAccessToken = (): string | null => {
  if (!isBrowser()) return null;
  const auth = readStoredAuth();
  return auth?.accessToken ?? null;
};

export const writeStoredAuth = (auth: StoredAuth): void => {
  if (!isBrowser()) return;
  const storage = auth.rememberMe ? localStorage : sessionStorage;
  const otherStorage = auth.rememberMe ? sessionStorage : localStorage;
  storage.setItem(STORAGE_KEY, JSON.stringify(auth));
  otherStorage.removeItem(STORAGE_KEY);
};

export const clearStoredAuth = (): void => {
  if (!isBrowser()) return;
  localStorage.removeItem(STORAGE_KEY);
  sessionStorage.removeItem(STORAGE_KEY);
};
