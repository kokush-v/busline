"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useSuspenseQuery } from "@tanstack/react-query";
import { ArrowLeftIcon, ArrowRightIcon, UsersIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { routes } from "@/lib/routes";
import {
  getTripPublic,
  getGetTripPublicQueryKey,
} from "@/generated/api/endpoints/trips/trips";
import type { SelectedStopInfo } from "@/components/forms/trip/types";
import { TripStopTimeline } from "./trip-stop-timeline";

const TripRouteMap = dynamic(
  () => import("@/components/trips/trip-route-map"),
  { ssr: false },
);

type TripDetailsProps = {
  tripId: string;
};

export function TripDetails({ tripId }: TripDetailsProps) {
  const { data: trip } = useSuspenseQuery({
    queryKey: getGetTripPublicQueryKey(tripId),
    queryFn: () => getTripPublic(tripId),
  });

  const stops = [...trip.trip_stops].sort(
    (a, b) => a.position_index - b.position_index,
  );
  const firstStop = stops[0];
  const lastStop = stops[stops.length - 1];

  const fromCity = firstStop?.stop.city.name ?? "—";
  const toCity = lastStop?.stop.city.name ?? "—";

  const mapStops: SelectedStopInfo[] = stops.map((ts) => ({
    id: ts.stop.id,
    name: ts.stop.name,
    latitude: ts.stop.latitude,
    longitude: ts.stop.longitude,
  }));

  return (
    <div className="space-y-6">
      <Button asChild variant="ghost" size="sm" className="gap-1">
        <Link href={routes.trips}>
          <ArrowLeftIcon className="size-4" />
          Back to trips
        </Link>
      </Button>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                {fromCity}
                <ArrowRightIcon className="size-4 shrink-0" />
                {toCity}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold">
                  {trip.price_per_seat} UAH
                </span>
                <span className="text-muted-foreground flex items-center gap-1 text-sm">
                  <UsersIcon className="size-3.5" />
                  {trip.seats_left} seats left
                </span>
              </div>
              <Button asChild className="w-full">
                <Link href={routes.tripBook(tripId)}>Book Now</Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Route</CardTitle>
            </CardHeader>
            <CardContent>
              <TripStopTimeline stops={trip.trip_stops} />
            </CardContent>
          </Card>
        </div>

        <div className="h-[400px] overflow-hidden rounded-lg border lg:h-auto lg:min-h-[500px]">
          <TripRouteMap stops={mapStops} />
        </div>
      </div>
    </div>
  );
}
