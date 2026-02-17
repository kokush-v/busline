"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { useTripsApi } from "@/hooks/use-trips-api";
import { TripForm } from "@/components/forms/trip";
import { Skeleton } from "@/components/ui/skeleton";
import { routes } from "@/lib/routes";
import type { TripFormValues } from "@/components/forms/trip/schema";
import type { SelectedStopInfo } from "@/components/forms/trip/types";
import type { StopRead } from "@/generated/api/model";

const TripRouteMap = dynamic(
  () => import("@/components/trips/trip-route-map"),
  {
    ssr: false,
    loading: () => <Skeleton className="h-full w-full" />,
  },
);

export default function TripNewPage() {
  const router = useRouter();
  const [selectedStops, setSelectedStops] = useState<SelectedStopInfo[]>([]);

  const { createTrip, isMutating } = useTripsApi();

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

  const handleSubmit = (data: TripFormValues) => {
    createTrip(
      {
        bus_id: data.bus_id,
        price_per_seat: data.price_per_seat,
        stops: data.stops.map((stop, index) => ({
          stop_id: stop.stop_id,
          position_index: index + 1,
          arrival_time: new Date(stop.arrival_time).toISOString(),
          departure_time: new Date(stop.departure_time).toISOString(),
        })),
      },
      () => router.push(routes.admin.trips),
    );
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-0">
      <div className="relative min-h-0 flex-1 overflow-hidden rounded-sm">
        <TripRouteMap stops={selectedStops} />
      </div>
      <div className="w-96 shrink-0">
        <TripForm
          selectedStops={selectedStops}
          onStopAdd={handleStopAdd}
          onStopRemove={handleStopRemove}
          onStopReorder={handleStopReorder}
          onSubmit={handleSubmit}
          onCancel={() => router.push(routes.admin.trips)}
          isMutating={isMutating}
        />
      </div>
    </div>
  );
}
