"use client";

import { TicketIcon } from "lucide-react";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";
import {
  formatDateShort,
  formatDateFull,
} from "@/components/analytics/analytics-chart";
import type { BookingsTimeSeriesPoint } from "@/generated/api/model";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  type ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Skeleton } from "@/components/ui/skeleton";

const bookingsConfig = {
  paid: { label: "Paid", color: "var(--chart-1)" },
  pending: { label: "Pending", color: "var(--chart-3)" },
  cancelled: { label: "Cancelled", color: "var(--chart-4)" },
  failed: { label: "Failed", color: "var(--chart-5)" },
} satisfies ChartConfig;

interface BookingsChartProps {
  data: BookingsTimeSeriesPoint[];
  isLoading: boolean;
  footer?: React.ReactNode;
}

export function BookingsChart({ data, isLoading, footer }: BookingsChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">
          <span className="inline-flex items-center gap-1.5">
            <TicketIcon className="text-muted-foreground size-4" />
            Bookings
          </span>
        </CardTitle>
        <CardDescription>Bookings breakdown by status</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-[200px] w-full" />
        ) : (
          <ChartContainer config={bookingsConfig} className="h-[200px] w-full">
            <AreaChart data={data} margin={{ left: 12, right: 12 }}>
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={formatDateShort}
              />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    indicator="line"
                    labelFormatter={formatDateFull}
                  />
                }
              />
              <Area
                dataKey="paid"
                type="natural"
                fill="var(--color-paid)"
                fillOpacity={0.4}
                stroke="var(--color-paid)"
                stackId="a"
              />
              <Area
                dataKey="pending"
                type="natural"
                fill="var(--color-pending)"
                fillOpacity={0.4}
                stroke="var(--color-pending)"
                stackId="a"
              />
              <Area
                dataKey="cancelled"
                type="natural"
                fill="var(--color-cancelled)"
                fillOpacity={0.4}
                stroke="var(--color-cancelled)"
                stackId="a"
              />
              <Area
                dataKey="failed"
                type="natural"
                fill="var(--color-failed)"
                fillOpacity={0.4}
                stroke="var(--color-failed)"
                stackId="a"
              />
              <ChartLegend content={<ChartLegendContent />} />
            </AreaChart>
          </ChartContainer>
        )}
      </CardContent>
      {footer && (
        <CardFooter className="text-muted-foreground text-sm">
          {footer}
        </CardFooter>
      )}
    </Card>
  );
}
