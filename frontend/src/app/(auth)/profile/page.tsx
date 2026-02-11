"use client";

import { useRouter } from "next/navigation";
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
import { ProtectedRoute } from "@/components/auth/protected-route";
import { ProfileForm } from "@/components/forms/profile";
import { UserOrderHistory } from "@/components/profile/user-order-history";
import { useAuth } from "@/components/auth/auth-provider";
import { routes } from "@/lib/routes";

export default function ProfilePage() {
  const { logout, isLoading } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    try {
      await logout();
      router.push(routes.login);
    } catch {
      toast.error("Unable to sign out. Please try again.");
    }
  };

  return (
    <ProtectedRoute>
      <main className="bg-background min-h-screen px-6 py-10">
        <div className="mx-auto flex max-w-5xl flex-col gap-8">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <Text role="h1">Your profile</Text>
              <Text role="muted">Review bookings and manage your data.</Text>
            </div>
            <Button
              variant="outline"
              type="button"
              onClick={handleSignOut}
              disabled={isLoading}
            >
              Sign out
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
              <CardDescription>View your contact details.</CardDescription>
            </CardHeader>
            <CardContent>
              <ProfileForm />
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <UserOrderHistory />
            </CardContent>
          </Card>
        </div>
      </main>
    </ProtectedRoute>
  );
}
