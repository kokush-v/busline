import { isBrowser } from "@/utils/common";
import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { getErrorMessage } from "./error-handler";

export const AXIOS_INSTANCE = axios.create({
  baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

AXIOS_INSTANCE.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const message = getErrorMessage(error);
    error.message = message;
    return Promise.reject(error);
  },
);

type CancellablePromise<T> = Promise<T> & { cancel: () => void };

export const httpInstance = <T>(
  config: AxiosRequestConfig,
  options?: AxiosRequestConfig,
): Promise<T> => {
  const source = axios.CancelToken.source();
  const token = isBrowser()
    ? (localStorage.getItem("token") ?? sessionStorage.getItem("token"))
    : null;

  const promise = AXIOS_INSTANCE({
    ...config,
    ...options,
    headers: {
      ...config.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
    cancelToken: source.token,
  }).then(({ data }) => data) as CancellablePromise<T>;

  promise.cancel = () => {
    source.cancel("Query was cancelled");
  };

  return promise;
};

export type ErrorType<Error> = AxiosError<Error>;

export type BodyType<Body> = Body;
