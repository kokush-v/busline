import { z } from "zod";

export const registerSchema = z
  .object({
    name: z.string().min(2, "Enter your name"),
    email: z.email("Enter a valid email"),
    password: z.string().min(8, "Minimum 8 characters"),
    confirmPassword: z.string().min(8, "Confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

export type RegisterFormValues = z.infer<typeof registerSchema>;
