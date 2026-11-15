"use client";

import { useParams } from "next/navigation";
import { useGetTrip } from "@/generated/api/endpoints/trips/trips";
import { TripEditForm } from "@/components/trips/trip-edit-form";
import { Spinner } from "@/components/ui/spinner";

export default function TripEditPage() {
  const params = useParams<{ id: string }>();
  const tripId = params.id;

  const { data: trip, isLoading: tripLoading } = useGetTrip(tripId);

  if (tripLoading) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!trip) {
    return (
      <div className="flex h-[calc(100vh-8rem)] items-center justify-center">
        <p className="text-muted-foreground">Trip not found.</p>
      </div>
    );
  }

  return <TripEditForm tripId={tripId} trip={trip} />;
}
