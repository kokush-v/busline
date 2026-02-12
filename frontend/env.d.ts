declare namespace NodeJS {
  interface ProcessEnv {
    /**
     * Backend API URL
     * @example "http://localhost:8080"
     */
    NEXT_PUBLIC_BACKEND_URL: string;
  }
}
