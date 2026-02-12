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
import { RegisterForm } from "@/components/forms/register";
import { PublicRoute } from "@/components/auth/public-route";
import { routes } from "@/lib/routes";

export default function RegisterPage() {
  return (
    <PublicRoute>
      <PageContainer>
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Create an account</CardTitle>
            <CardDescription>
              Sign up to book trips and manage your orders.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <RegisterForm />
            <p className="text-muted-foreground text-center text-sm">
              Already have an account?{" "}
              <Link href={routes.login} className="text-primary">
                Sign in
              </Link>
            </p>
          </CardContent>
        </Card>
      </PageContainer>
    </PublicRoute>
  );
}
