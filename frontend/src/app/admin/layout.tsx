"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboardIcon, MapPinIcon, BusIcon } from "lucide-react";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { PageContainer } from "@/components/ui/page-container";
import { Text } from "@/components/ui/text";
import { routes } from "@/lib/routes";
import { cn } from "@/lib/utils";

const adminNavItems = [
  {
    label: "Dashboard",
    href: routes.admin.dashboard,
    icon: LayoutDashboardIcon,
  },
  {
    label: "Cities",
    href: routes.admin.cities,
    icon: MapPinIcon,
  },
  {
    label: "Buses",
    href: routes.admin.buses,
    icon: BusIcon,
  },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute roles={["ADMIN"]}>
      <div className="flex min-h-[calc(100vh-4rem)]">
        <AdminSidebar />
        <PageContainer
          centered={false}
          className="min-h-0 min-w-0 flex-1 px-3 py-8 sm:px-4"
        >
          {children}
        </PageContainer>
      </div>
    </ProtectedRoute>
  );
}

function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="bg-muted/40 hidden w-60 shrink-0 border-r md:block">
      <div className="flex h-full flex-col gap-2 p-4">
        <div className="mb-4 flex items-center gap-2 px-2">
          <Text role="h4">Admin Panel</Text>
        </div>

        <nav className="flex flex-1 flex-col gap-1">
          {adminNavItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Button
                key={item.href}
                asChild
                variant={isActive ? "secondary" : "ghost"}
                className={cn("justify-start", isActive && "font-semibold")}
              >
                <Link href={item.href}>
                  <item.icon className="size-4" />
                  {item.label}
                </Link>
              </Button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
