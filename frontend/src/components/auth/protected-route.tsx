"use client";

import { useEffect } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/components/auth/auth-provider";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
	const { isAuthenticated, isLoading } = useAuth();
	const router = useRouter();
	const pathname = usePathname();
	const searchParams = useSearchParams();

	useEffect(() => {
		if (!isLoading && !isAuthenticated) {
			const next = `${pathname}${searchParams.toString() ? `?${searchParams}` : ""}`;
			router.replace(`/login?next=${encodeURIComponent(next)}`);
		}
	}, [isAuthenticated, isLoading, pathname, router, searchParams]);

	if (!isAuthenticated) {
		return null;
	}

	return <>{children}</>;
}
