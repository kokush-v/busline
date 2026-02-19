"use client";

import { useMemo } from "react";
import { XIcon } from "lucide-react";
import { Combobox } from "@/components/ui/combobox";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { TripDateFilter } from "@/components/trips/trip-date-filter";
import { useGetSearchStops } from "@/generated/api/endpoints/stops/stops";
import type { TripSortBy, SortOrder } from "@/generated/api/model";

type TripFiltersProps = {
  fromStopId: string;
  toStopId: string;
  departureDateFrom: string;
  departureDateTo: string;
  sortBy: TripSortBy;
  sortOrder: SortOrder;
  onFromStopChange: (value: string) => void;
  onToStopChange: (value: string) => void;
  onDepartureDateFromChange: (value: string) => void;
  onDepartureDateToChange: (value: string) => void;
  onSortChange: (sortBy: TripSortBy, sortOrder: SortOrder) => void;
};

const SORT_OPTIONS = [
  { value: "departure_time:asc", label: "Departure (earliest)" },
  { value: "departure_time:desc", label: "Departure (latest)" },
  { value: "price:asc", label: "Price (low to high)" },
  { value: "price:desc", label: "Price (high to low)" },
  { value: "seats_left:desc", label: "Seats (most first)" },
  { value: "seats_left:asc", label: "Seats (fewest first)" },
] as const;

export function TripFilters({
  fromStopId,
  toStopId,
  departureDateFrom,
  departureDateTo,
  sortBy,
  sortOrder,
  onFromStopChange,
  onToStopChange,
  onDepartureDateFromChange,
  onDepartureDateToChange,
  onSortChange,
}: TripFiltersProps) {
  const { data: stopsData, isLoading: stopsLoading } = useGetSearchStops({
    limit: 100,
  });

  const stopOptions = useMemo(() => {
    if (!stopsData?.items) return [];
    return stopsData.items.map((s) => ({
      value: s.id,
      label: `${s.name} (${s.city_name})`,
    }));
  }, [stopsData]);

  const currentSortValue = `${sortBy}:${sortOrder}`;
  const hasStopFilters = fromStopId || toStopId;

  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="w-64 space-y-1">
        <Label className="text-xs">From</Label>
        <Combobox
          options={stopOptions}
          value={fromStopId}
          onChange={onFromStopChange}
          placeholder="Any stop"
          isLoading={stopsLoading}
        />
      </div>

      <div className="w-64 space-y-1">
        <Label className="text-xs">To</Label>
        <Combobox
          options={stopOptions}
          value={toStopId}
          onChange={onToStopChange}
          placeholder="Any stop"
          isLoading={stopsLoading}
        />
      </div>

      {hasStopFilters && (
        <Button
          variant="ghost"
          size="icon"
          className="size-9"
          onClick={() => {
            onFromStopChange("");
            onToStopChange("");
          }}
        >
          <XIcon className="size-4" />
        </Button>
      )}

      <TripDateFilter
        departureDateFrom={departureDateFrom}
        departureDateTo={departureDateTo}
        onDepartureDateFromChange={onDepartureDateFromChange}
        onDepartureDateToChange={onDepartureDateToChange}
      />

      <div className="space-y-1">
        <Label className="text-xs">Sort by</Label>
        <select
          value={currentSortValue}
          onChange={(e) => {
            const [newSortBy, newSortOrder] = e.target.value.split(":") as [
              TripSortBy,
              SortOrder,
            ];
            onSortChange(newSortBy, newSortOrder);
          }}
          className="border-input bg-background ring-offset-background h-9 rounded-md border px-3 text-sm focus:ring-2 focus:outline-none"
        >
          {SORT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
