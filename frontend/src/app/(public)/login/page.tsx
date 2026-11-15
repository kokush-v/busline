"use client";

import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PageContainer } from "@/components/ui/page-container";
import { LoginForm } from "@/components/forms/login";
import { PublicRoute } from "@/components/auth/public-route";
import { routes } from "@/lib/routes";

export default function LoginPage() {
  return (
    <PublicRoute>
      <PageContainer>
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
      </PageContainer>
    </PublicRoute>
  );
}
