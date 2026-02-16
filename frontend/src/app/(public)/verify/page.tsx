"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PageContainer } from "@/components/ui/page-container";
import { VerifyForm } from "@/components/forms/verify";
import { PublicRoute } from "@/components/auth/public-route";

export default function VerifyPage() {
  return (
    <PublicRoute>
      <PageContainer>
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Verify your account</CardTitle>
            <CardDescription>
              Enter the code sent to your email.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <VerifyForm />
          </CardContent>
        </Card>
      </PageContainer>
    </PublicRoute>
  );
}
