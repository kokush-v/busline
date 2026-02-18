"use client";

import type { LucideIcon } from "lucide-react";
import { ArrowRightIcon } from "lucide-react";
import Link from "next/link";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";
import type { TimeSeriesPoint } from "@/generated/api/model";
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
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Skeleton } from "@/components/ui/skeleton";

function parseWeekToRange(value: string): [Date, Date] | null {
  const match = value.match(/^(\d{4})-W(\d{2})$/);
  if (!match) return null;
  const year = Number(match[1]);
  const week = Number(match[2]);
  // ISO week: Jan 4 is always in week 1
  const jan4 = new Date(year, 0, 4);
  const dayOfWeek = jan4.getDay() || 7; // Mon=1..Sun=7
  const monday = new Date(jan4);
  monday.setDate(jan4.getDate() - dayOfWeek + 1 + (week - 1) * 7);
  const sunday = new Date(monday);
  sunday.setDate(monday.getDate() + 6);
  return [monday, sunday];
}

function parseMonth(value: string): Date | null {
  const match = value.match(/^(\d{4})-(\d{2})$/);
  if (!match) return null;
  return new Date(Number(match[1]), Number(match[2]) - 1);
}

function formatDateShort(value: string) {
  const weekRange = parseWeekToRange(value);
  if (weekRange) {
    const fmt = (d: Date) =>
      d.toLocaleDateString("uk-UA", { month: "short", day: "numeric" });
    return `${fmt(weekRange[0])} – ${fmt(weekRange[1])}`;
  }
  const month = parseMonth(value);
  if (month) {
    return month.toLocaleDateString("uk-UA", {
      month: "short",
      year: "numeric",
    });
  }
  const date = new Date(value);
  if (isNaN(date.getTime())) return value;
  return date.toLocaleDateString("uk-UA", { month: "short", day: "numeric" });
}

function formatDateFull(value: string) {
  const weekRange = parseWeekToRange(value);
  if (weekRange) {
    const fmt = (d: Date) =>
      d.toLocaleDateString("uk-UA", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    return `${fmt(weekRange[0])} – ${fmt(weekRange[1])}`;
  }
  const month = parseMonth(value);
  if (month) {
    return month.toLocaleDateString("uk-UA", {
      month: "long",
      year: "numeric",
    });
  }
  const date = new Date(value);
  if (isNaN(date.getTime())) return value;
  return date.toLocaleDateString("uk-UA", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export { formatDateShort, formatDateFull };

interface AnalyticsChartProps {
  title: string;
  description: string;
  icon: LucideIcon;
  href?: string;
  data: TimeSeriesPoint[];
  config: ChartConfig;
  isLoading: boolean;
  valueFormatter?: (value: string) => string;
  footer?: React.ReactNode;
}

export function AnalyticsChart({
  title,
  description,
  icon: Icon,
  href,
  data,
  config,
  isLoading,
  valueFormatter,
  footer,
}: AnalyticsChartProps) {
  const dataKey = Object.keys(config)[0];

  const chartData = data.map((point) => ({
    date: point.date,
    [dataKey]: Number(point.value),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">
          {href ? (
            <Link
              href={href}
              className="group/link text-foreground inline-flex items-center gap-1.5"
            >
              <Icon className="text-muted-foreground size-4" />
              <span className="group-hover/link:underline">{title}</span>
              <ArrowRightIcon className="text-muted-foreground size-3" />
            </Link>
          ) : (
            <span className="inline-flex items-center gap-1.5">
              <Icon className="text-muted-foreground size-4" />
              {title}
            </span>
          )}
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <Skeleton className="h-[200px] w-full" />
        ) : (
          <ChartContainer config={config} className="h-[200px] w-full">
            <AreaChart data={chartData}>
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
                    labelFormatter={formatDateFull}
                    formatter={
                      valueFormatter
                        ? (value) => valueFormatter(String(value))
                        : undefined
                    }
                  />
                }
              />
              <Area
                dataKey={dataKey}
                type="natural"
                fill={`var(--color-${dataKey})`}
                fillOpacity={0.4}
                stroke={`var(--color-${dataKey})`}
                stackId="a"
              />
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
