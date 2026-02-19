"use client";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { ProfileForm } from "@/components/forms/profile";
import { UserOrderHistory } from "@/components/profile/user-order-history";
import { ProfilePageContent } from "@/components/profile/profile-content";

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfilePageContent>
        <ProfileForm />
        <UserOrderHistory />
      </ProfilePageContent>
    </ProtectedRoute>
  );
}
