"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/components/auth/auth-provider";
import { getErrorMessage } from "@/lib/api/error-handler";
import { routes } from "@/lib/routes";
import { loginSchema, type LoginFormValues } from "./schema";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isLoading } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: true,
    },
  });

  const [rememberMe, setRememberMe] = useState(true);

  const onSubmit = handleSubmit(async (data) => {
    try {
      await login({
        email: data.email,
        password: data.password,
        rememberMe: data.rememberMe ?? false,
      });
      const next = searchParams.get("next");
      router.push(next || routes.profile);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <FormField id="email" label="Email" error={errors.email?.message}>
        <Input
          id="email"
          type="email"
          placeholder="you@email.com"
          {...register("email")}
        />
      </FormField>
      <FormField
        id="password"
        label="Password"
        error={errors.password?.message}
      >
        <Input id="password" type="password" {...register("password")} />
      </FormField>
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm">
          <Checkbox
            checked={rememberMe}
            onCheckedChange={(value) => {
              const nextValue = Boolean(value);
              setRememberMe(nextValue);
              setValue("rememberMe", nextValue);
            }}
          />
          Remember me
        </label>
      </div>
      <Button className="w-full" type="submit" disabled={isLoading}>
        Sign in
      </Button>
    </form>
  );
}
