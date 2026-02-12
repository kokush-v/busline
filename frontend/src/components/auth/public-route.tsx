"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/auth/auth-provider";
import { routes } from "@/lib/routes";

export function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  if (isAuthenticated) {
    const next = searchParams.get("next");
    router.replace(next || routes.home);
    return null;
  }

  return <>{children}</>;
}
