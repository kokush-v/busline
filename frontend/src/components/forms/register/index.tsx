"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/components/auth/auth-provider";
import { getErrorMessage } from "@/lib/api/error-handler";
import { routes } from "@/lib/routes";
import { AuthCode } from "@/generated/api/model";
import { registerSchema, type RegisterFormValues } from "./schema";

export function RegisterForm() {
  const router = useRouter();
  const { register: registerUser } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = handleSubmit(async (data) => {
    try {
      const response = await registerUser({
        email: data.email,
        password: data.password,
        name: data.name,
        phone_number: "",
      });
      toast.success("Registration successful. Check your email.");
      if (response?.code === AuthCode.SIGN_UP_SUCCESS) {
        router.push(`${routes.verify}?email=${encodeURIComponent(data.email)}`);
      } else {
        router.push(routes.login);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <FormField id="name" label="Name" error={errors.name?.message}>
        <Input id="name" {...register("name")} />
      </FormField>
      <FormField id="email" label="Email" error={errors.email?.message}>
        <Input id="email" type="email" {...register("email")} />
      </FormField>
      <FormField
        id="password"
        label="Password"
        error={errors.password?.message}
      >
        <Input id="password" type="password" {...register("password")} />
      </FormField>
      <FormField
        id="confirmPassword"
        label="Confirm password"
        error={errors.confirmPassword?.message}
      >
        <Input
          id="confirmPassword"
          type="password"
          {...register("confirmPassword")}
        />
      </FormField>
      <Button className="w-full" type="submit" disabled={isSubmitting}>
        Create account
      </Button>
    </form>
  );
}
