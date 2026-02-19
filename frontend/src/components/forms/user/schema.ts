import { z } from "zod";
import { UserRoleGroups } from "@/generated/api/model/userRoleGroups";

export const userCreateSchema = z.object({
  email: z.string().email("Valid email is required"),
  name: z.string().optional(),
  phone_number: z.string().optional(),
  role: z.nativeEnum(UserRoleGroups).default(UserRoleGroups.USER),
});

export type UserCreateFormValues = z.infer<typeof userCreateSchema>;

export const userUpdateSchema = z.object({
  name: z.string().optional(),
  phone_number: z.string().optional(),
  role: z.nativeEnum(UserRoleGroups),
  is_active: z.boolean(),
});

export type UserUpdateFormValues = z.infer<typeof userUpdateSchema>;
