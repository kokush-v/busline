"use client";

import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";

type ProfileFormValues = {
  name: string;
  email: string;
  phone: string;
};

export function ProfileForm() {
  const { user } = useAuth();

  const profileValues: ProfileFormValues = {
    name: user?.name ?? "—",
    email: user?.email ?? "—",
    phone: user?.phone_number ?? "—",
  };

  if (!user) {
    return (
      <p className="text-muted-foreground text-sm">
        Profile data is unavailable right now.
      </p>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="grid gap-2">
        <label htmlFor="name" className="text-sm font-medium">
          Name
        </label>
        <Input id="name" value={profileValues.name} readOnly />
      </div>
      <div className="grid gap-2">
        <label htmlFor="email" className="text-sm font-medium">
          Email
        </label>
        <Input id="email" type="email" value={profileValues.email} readOnly />
      </div>
      <div className="grid gap-2">
        <label htmlFor="phone" className="text-sm font-medium">
          Phone
        </label>
        <Input id="phone" value={profileValues.phone} readOnly />
      </div>
    </div>
  );
}
