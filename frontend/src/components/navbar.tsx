"use client";

import Link from "next/link";
import { UserIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/components/auth/auth-provider/use-auth";
import { routes } from "@/lib/routes";

export function Navbar() {
  const { isAuthenticated } = useAuth();

  const renderAuthBlock = () => {
    if (isAuthenticated) {
      return (
        <Button asChild variant="ghost" size="icon">
          <Link href={routes.profile} aria-label="Profile">
            <UserIcon className="size-5" />
          </Link>
        </Button>
      );
    }

    return (
      <Button asChild variant="default">
        <Link href={routes.login}>Sign In</Link>
      </Button>
    );
  };

  return (
    <nav className="bg-background sticky top-0 z-50 border-b">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link href={routes.home} className="flex items-center gap-2">
          <div className="text-primary text-xl font-bold">BusLine</div>
        </Link>
        {renderAuthBlock()}
      </div>
    </nav>
  );
}
