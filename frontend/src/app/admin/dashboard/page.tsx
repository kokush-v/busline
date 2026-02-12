"use client";

import Link from "next/link";
import { MapPinIcon, UsersIcon, RouteIcon, BarChartIcon } from "lucide-react";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Text } from "@/components/ui/text";
import { useAuth } from "@/hooks/use-auth";
import { routes } from "@/lib/routes";

const quickLinks = [
  {
    title: "Cities",
    description: "Manage cities available in the system.",
    href: routes.admin.cities,
    icon: MapPinIcon,
  },
  {
    title: "Users",
    description: "Manage user accounts and roles.",
    href: "#",
    icon: UsersIcon,
    disabled: true,
  },
  {
    title: "Routes",
    description: "Manage bus routes and schedules.",
    href: "#",
    icon: RouteIcon,
    disabled: true,
  },
  {
    title: "Analytics",
    description: "View system statistics and reports.",
    href: "#",
    icon: BarChartIcon,
    disabled: true,
  },
];

export default function AdminDashboardPage() {
  const { user } = useAuth();

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-8">
      <div>
        <Text role="h2">Dashboard</Text>
        <Text role="muted">
          Welcome back, {user?.name ?? user?.email ?? "Admin"}.
        </Text>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {quickLinks.map((item) => {
          const content = (
            <Card
              key={item.title}
              className={
                item.disabled
                  ? "opacity-50"
                  : "hover:border-primary/50 transition-colors"
              }
            >
              <CardHeader className="flex flex-row items-center gap-3">
                <item.icon className="text-primary size-5" />
                <div>
                  <CardTitle className="text-base">{item.title}</CardTitle>
                  <CardDescription>{item.description}</CardDescription>
                </div>
              </CardHeader>
            </Card>
          );

          if (item.disabled) {
            return (
              <div key={item.title} className="cursor-not-allowed">
                {content}
              </div>
            );
          }

          return (
            <Link key={item.title} href={item.href}>
              {content}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
