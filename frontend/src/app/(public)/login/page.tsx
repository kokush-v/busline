"use client";

import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { LoginForm } from "@/components/forms/login";
import { routes } from "@/lib/routes";

export default function LoginPage() {
  return (
    <main className="bg-background flex min-h-screen items-center justify-center px-6 py-12">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Sign in to BusLine</CardTitle>
          <CardDescription>
            Enter your details to access your account.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <LoginForm />
          <p className="text-muted-foreground text-center text-sm">
            Don&apos;t have an account?{" "}
            <Link href={routes.register} className="text-primary">
              Create one
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
