import Image from "next/image";
import Link from "next/link";
import { ArrowRightIcon, BusIcon, ClockIcon, UsersIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { routes } from "@/lib/routes";
import type { TripReadPublic } from "@/generated/api/model";

type TripCardProps = {
  trip: TripReadPublic;
};

export function TripCard({ trip }: TripCardProps) {
  const stops = trip.trip_stops;
  const firstStop = stops[0];
  const lastStop = stops[stops.length - 1];

  const fromCity = firstStop?.stop.city.name ?? "—";
  const toCity = lastStop?.stop.city.name ?? "—";

  const departureTime = firstStop
    ? new Date(firstStop.departure_time).toLocaleString("en-GB", {
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";

  const photoUrl = trip.bus.photo_url;

  return (
    <Card className="flex h-full flex-col overflow-hidden pt-0">
      {photoUrl ? (
        <div className="relative h-40 w-full">
          <Image
            src={photoUrl}
            alt="Bus"
            fill
            className="object-cover"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        </div>
      ) : (
        <div className="bg-muted flex h-40 items-center justify-center">
          <BusIcon className="text-muted-foreground size-10" />
        </div>
      )}
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          {fromCity}
          <ArrowRightIcon className="size-4 shrink-0" />
          {toCity}
        </CardTitle>
        <p className="text-muted-foreground flex items-center gap-1.5 text-sm">
          <ClockIcon className="size-3.5" />
          {departureTime}
        </p>
      </CardHeader>
      <CardContent className="mt-auto space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="font-semibold">{trip.price_per_seat} UAH</span>
          <span className="text-muted-foreground flex items-center gap-1">
            <UsersIcon className="size-3.5" />
            {trip.seats_left} seats
          </span>
        </div>
        <Button asChild className="w-full" variant="outline" size="sm">
          <Link href={routes.tripDetails(trip.id)}>View details</Link>
        </Button>
      </CardContent>
    </Card>
  );
}
