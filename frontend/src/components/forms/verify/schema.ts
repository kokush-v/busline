import { z } from "zod";

export const verifySchema = z.object({
  email: z.email("Enter your email"),
  code: z.string().min(4, "Enter the code"),
});

export type VerifyFormValues = z.infer<typeof verifySchema>;
