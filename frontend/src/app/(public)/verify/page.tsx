"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { VerifyForm } from "@/components/forms/verify";

export default function VerifyPage() {
  return (
    <main className="bg-background flex min-h-screen items-center justify-center px-6 py-12">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Verify your account</CardTitle>
          <CardDescription>Enter the code sent to your email.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <VerifyForm />
        </CardContent>
      </Card>
    </main>
  );
}
