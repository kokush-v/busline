"use client";

import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import { RefreshCwIcon } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Text } from "@/components/ui/text";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { routes } from "@/lib/routes";
import { UserRoleGroups } from "@/generated/api/model";
import Link from "next/link";

export function ProfilePageContent({
  children,
}: {
  children: [React.ReactNode, React.ReactNode];
}) {
  const { logout, user, authError } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  const handleSignOut = async () => {
    try {
      await logout();
      router.push(routes.login);
    } catch {
      toast.error("Unable to sign out. Please try again.");
    }
  };

  const [profileForm, orderHistory] = children;

  if (authError) {
    return (
      <main className="bg-background min-h-screen px-6 py-10">
        <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center gap-3 text-center">
          <Text role="muted">{authError.message}</Text>
          <Button
            variant="outline"
            size="icon-sm"
            onClick={() =>
              queryClient.invalidateQueries({ queryKey: ["auth", "session"] })
            }
            aria-label="Try again"
          >
            <RefreshCwIcon />
          </Button>
        </div>
      </main>
    );
  }

  return (
    <main className="bg-background min-h-screen px-6 py-10">
      <div className="mx-auto flex max-w-5xl flex-col gap-8">
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div>
            <Text role="h1">Your profile</Text>
            <Text role="muted">Review bookings and manage your data.</Text>
          </div>
          <Button variant="outline" type="button" onClick={handleSignOut}>
            Sign out
          </Button>
        </div>

        {user?.role === UserRoleGroups.ADMIN && (
          <Card>
            <CardHeader>
              <CardTitle>Admin Panel</CardTitle>
              <CardDescription>
                Manage cities, users, and system settings.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild>
                <Link href={routes.admin.dashboard}>Open Admin Panel</Link>
              </Button>
            </CardContent>
          </Card>
        )}
        <Card>
          <CardHeader>
            <CardTitle>Profile</CardTitle>
            <CardDescription>View your contact details.</CardDescription>
          </CardHeader>
          <CardContent>{profileForm}</CardContent>
        </Card>

        {orderHistory}
      </div>
    </main>
  );
}
