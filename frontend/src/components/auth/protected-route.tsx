"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { routes } from "@/lib/routes";
import type { UserRoleGroups } from "@/generated/api/model";

interface ProtectedRouteProps {
  children: React.ReactNode;
  roles?: UserRoleGroups[];
}

export function ProtectedRoute({ children, roles }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  if (!isAuthenticated) {
    const next = `${pathname}${searchParams.toString() ? `?${searchParams}` : ""}`;
    router.replace(`${routes.login}?next=${encodeURIComponent(next)}`);
    return null;
  }

  if (roles && (!user?.role || !roles.includes(user.role))) {
    router.replace(routes.profile);
    return null;
  }

  return <>{children}</>;
}
