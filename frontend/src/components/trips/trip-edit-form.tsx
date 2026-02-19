"use client";

import { useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { useGetStops } from "@/generated/api/endpoints/stops/stops";
import { useTripsApi } from "@/hooks/use-trips-api";
import { TripForm } from "@/components/forms/trip";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { routes } from "@/lib/routes";
import type { TripFormValues } from "@/components/forms/trip/schema";
import type { SelectedStopInfo } from "@/components/forms/trip/types";
import type { TripRead, StopRead } from "@/generated/api/model";

const TripRouteMap = dynamic(
  () => import("@/components/trips/trip-route-map"),
  {
    ssr: false,
    loading: () => <Skeleton className="h-full w-full" />,
  },
);

export function TripEditForm({
  tripId,
  trip,
}: {
  tripId: string;
  trip: TripRead;
}) {
  const router = useRouter();
  const { data: stopsData, isLoading: stopsLoading } = useGetStops({
    limit: 100,
  });
  const allStops = useMemo(() => stopsData?.items ?? [], [stopsData?.items]);
  const { updateTrip, isMutating } = useTripsApi();

  const sortedTripStops = useMemo(
    () =>
      [...trip.trip_stops].sort((a, b) => a.position_index - b.position_index),
    [trip.trip_stops],
  );

  const defaultValues = useMemo(
    () => ({
      bus_id: trip.bus_id,
      price_per_seat: trip.price_per_seat,
      stops: sortedTripStops.map((ts) => ({
        stop_id: ts.stop_id,
        arrival_time: ts.arrival_time.slice(0, 16),
        departure_time: ts.departure_time.slice(0, 16),
      })),
    }),
    [trip, sortedTripStops],
  );

  const initialSelectedStops = useMemo(
    () =>
      sortedTripStops
        .map((ts) => {
          const stop = allStops.find((s) => s.id === ts.stop_id);
          if (!stop) return null;
          return {
            id: stop.id,
            name: stop.name,
            latitude: stop.latitude,
            longitude: stop.longitude,
          };
        })
        .filter(Boolean) as SelectedStopInfo[],
    [sortedTripStops, allStops],
  );

  if (stopsLoading) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <Spinner />
      </div>
    );
  }

  return (
    <TripEditFormInner
      tripId={tripId}
      defaultValues={defaultValues}
      initialSelectedStops={initialSelectedStops}
      isMutating={isMutating}
      onSubmit={(data) => {
        updateTrip(tripId, {
          price_per_seat: data.price_per_seat,
          stops: data.stops.map((stop, index) => ({
            stop_id: stop.stop_id,
            position_index: index + 1,
            arrival_time: new Date(stop.arrival_time).toISOString(),
            departure_time: new Date(stop.departure_time).toISOString(),
          })),
        });
      }}
      onCancel={() => router.push(routes.admin.trips)}
    />
  );
}

function TripEditFormInner({
  tripId,
  defaultValues,
  initialSelectedStops,
  isMutating,
  onSubmit,
  onCancel,
}: {
  tripId: string;
  defaultValues: TripFormValues;
  initialSelectedStops: SelectedStopInfo[];
  isMutating: boolean;
  onSubmit: (data: TripFormValues) => void;
  onCancel: () => void;
}) {
  const [selectedStops, setSelectedStops] =
    useState<SelectedStopInfo[]>(initialSelectedStops);

  const handleStopAdd = useCallback((stop: StopRead) => {
    setSelectedStops((prev) => {
      if (prev.some((s) => s.id === stop.id)) return prev;
      return [
        ...prev,
        {
          id: stop.id,
          name: stop.name,
          latitude: stop.latitude,
          longitude: stop.longitude,
        },
      ];
    });
  }, []);

  const handleStopRemove = useCallback((stopId: string) => {
    setSelectedStops((prev) => prev.filter((s) => s.id !== stopId));
  }, []);

  const handleStopReorder = useCallback(
    (fromIndex: number, toIndex: number) => {
      setSelectedStops((prev) => {
        const next = [...prev];
        const [moved] = next.splice(fromIndex, 1);
        next.splice(toIndex, 0, moved);
        return next;
      });
    },
    [],
  );

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-0">
      <div className="relative min-h-0 flex-1 overflow-hidden rounded-sm">
        <TripRouteMap stops={selectedStops} />
      </div>
      <div className="w-96 shrink-0">
        <TripForm
          key={tripId}
          defaultValues={defaultValues}
          selectedStops={selectedStops}
          onStopAdd={handleStopAdd}
          onStopRemove={handleStopRemove}
          onStopReorder={handleStopReorder}
          onSubmit={onSubmit}
          onCancel={onCancel}
          isMutating={isMutating}
          isEdit
        />
      </div>
    </div>
  );
}
