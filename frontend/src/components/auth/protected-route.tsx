"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/auth/auth-provider";
import { routes } from "@/lib/routes";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  if (!isAuthenticated) {
    const next = `${pathname}${searchParams.toString() ? `?${searchParams}` : ""}`;
    router.replace(`${routes.login}?next=${encodeURIComponent(next)}`);
    return null;
  }

  return <>{children}</>;
}
