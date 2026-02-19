"use client";

import { useState } from "react";
import { BanknoteIcon, RouteIcon, UsersIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/hooks/use-auth";
import { routes } from "@/lib/routes";
import { AnalyticsChart } from "@/components/analytics/analytics-chart";
import { BookingsChart } from "@/components/analytics/bookings-chart";
import {
  useGetRevenueStats,
  useGetBookingsStats,
  useGetTripsStats,
  useGetUsersStats,
} from "@/generated/api/endpoints/analytics/analytics";
import type { AnalyticsPeriod } from "@/generated/api/model";
import type { ChartConfig } from "@/components/ui/chart";

const periodLabels: Record<AnalyticsPeriod, string> = {
  day: "Day",
  week: "Week",
  month: "Month",
};

const revenueConfig = {
  revenue: { label: "Revenue", color: "var(--chart-1)" },
} satisfies ChartConfig;

const tripsConfig = {
  trips: { label: "Trips", color: "var(--chart-3)" },
} satisfies ChartConfig;

const usersConfig = {
  users: { label: "Users", color: "var(--chart-4)" },
} satisfies ChartConfig;

function formatCurrency(value: string) {
  return `${Number(value).toLocaleString("uk-UA")} ₴`;
}

export default function AdminDashboardPage() {
  const { user } = useAuth();
  const [period, setPeriod] = useState<AnalyticsPeriod>("month");

  const revenue = useGetRevenueStats({ period });
  const bookings = useGetBookingsStats({ period });
  const trips = useGetTripsStats({ period });
  const users = useGetUsersStats({ period });

  return (
    <div className="flex w-full flex-col gap-8">
      <div>
        <Text role="h2">Dashboard</Text>
        <Text role="muted">
          Welcome back, {user?.name ?? user?.email ?? "Admin"}.
        </Text>
      </div>

      <Tabs
        value={period}
        onValueChange={(v) => setPeriod(v as AnalyticsPeriod)}
      >
        <TabsList>
          {(Object.keys(periodLabels) as AnalyticsPeriod[]).map((key) => (
            <TabsTrigger key={key} value={key}>
              {periodLabels[key]}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      <div className="grid gap-4 sm:grid-cols-2">
        <AnalyticsChart
          title="Revenue"
          description="Total revenue over time"
          icon={BanknoteIcon}
          data={revenue.data?.time_series ?? []}
          config={revenueConfig}
          isLoading={revenue.isLoading}
          valueFormatter={formatCurrency}
          footer={
            revenue.data && (
              <span>
                Total: {formatCurrency(revenue.data.summary.total_revenue)}
              </span>
            )
          }
        />
        <BookingsChart
          data={bookings.data?.time_series ?? []}
          isLoading={bookings.isLoading}
          footer={
            bookings.data && (
              <span>
                Total: {bookings.data.summary.total_orders} &middot; Paid:{" "}
                {bookings.data.summary.paid_count} &middot; Pending:{" "}
                {bookings.data.summary.pending_count} &middot; Cancelled:{" "}
                {bookings.data.summary.cancelled_count} &middot; Failed:{" "}
                {bookings.data.summary.failed_count}
              </span>
            )
          }
        />
        <AnalyticsChart
          title="Trips"
          description="Number of trips over time"
          icon={RouteIcon}
          href={routes.admin.trips}
          data={trips.data?.time_series ?? []}
          config={tripsConfig}
          isLoading={trips.isLoading}
          footer={
            trips.data && (
              <span>
                Total trips: {trips.data.summary.total_trips} &middot; Tickets
                sold: {trips.data.summary.total_tickets_sold}
              </span>
            )
          }
        />
        <AnalyticsChart
          title="Users"
          description="New user registrations over time"
          icon={UsersIcon}
          href={routes.admin.users}
          data={users.data?.time_series ?? []}
          config={usersConfig}
          isLoading={users.isLoading}
          footer={
            users.data && (
              <span>
                Total: {users.data.summary.total_users} &middot; Active:{" "}
                {users.data.summary.active_users}
              </span>
            )
          }
        />
      </div>
    </div>
  );
}
