"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";
import { getErrorMessage } from "@/lib/api/error-handler";
import { routes } from "@/lib/routes";
import { verifySchema, type VerifyFormValues } from "./schema";

export function VerifyForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { verify } = useAuth();
  const emailFromQuery = searchParams.get("email") ?? "";

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<VerifyFormValues>({
    resolver: zodResolver(verifySchema),
    defaultValues: {
      email: emailFromQuery,
    },
  });

  const onSubmit = handleSubmit(async (data) => {
    try {
      await verify({ email: data.email, code: data.code });
      toast.success("Account verified. Please sign in.");
      router.push(routes.login);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <FormField id="email" label="Email" error={errors.email?.message}>
        <Input id="email" type="email" {...register("email")} />
      </FormField>
      <FormField
        id="code"
        label="Verification code"
        error={errors.code?.message}
      >
        <Input id="code" {...register("code")} />
      </FormField>
      <Button className="w-full" type="submit">
        Verify
      </Button>
    </form>
  );
}
