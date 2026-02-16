import type { AxiosError } from "axios";
import { toast } from "sonner";
import type { ErrorSchema } from "@/types/error";
import type { HTTPValidationError } from "@/generated/api/model";

export type ApiError = ErrorSchema | HTTPValidationError;

export const getErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    // Axios error

    const axiosError = error as AxiosError<ApiError>;
    const data = axiosError.response?.data;

    if (!data) {
      return axiosError.message || "An error occurred";
    }

    console.log("Error data:", data);

    // Handle ErrorSchema
    if ("message" in data) {
      return (data as ErrorSchema).message;
    }

    // Handle HTTPValidationError
    if ("detail" in data) {
      const validationError = data as HTTPValidationError;
      if (validationError.detail && validationError.detail.length > 0) {
        return validationError.detail[0].msg;
      }
      return "Validation error";
    }

    return "An error occurred";
  }

  return String(error) || "An unknown error occurred";
};
