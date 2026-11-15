export interface ErrorSchema {
  message: string;
  code?: string | null;
  details?: Record<string, unknown> | null;
  timestamp: string;
}
