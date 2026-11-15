"use client";

import { Suspense } from "react";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getTripSeats,
  getGetTripSeatsQueryKey,
} from "@/generated/api/endpoints/trips/trips";
import { SeatGrid } from "./seat-grid";

type SeatSelectionStepProps = {
  tripId: string;
  selectedSeatIds: string[];
  onToggleSeat: (seatId: string) => void;
  onBack: () => void;
  onNext: () => void;
};

export function SeatSelectionStep({
  tripId,
  selectedSeatIds,
  onToggleSeat,
  onBack,
  onNext,
}: SeatSelectionStepProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Choose Your Seats</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Suspense fallback={<SeatGridSkeleton />}>
          <SeatGridLoader
            tripId={tripId}
            selectedSeatIds={selectedSeatIds}
            onToggleSeat={onToggleSeat}
          />
        </Suspense>

        <p className="text-muted-foreground text-center text-sm">
          {selectedSeatIds.length} seat(s) selected
        </p>

        <div className="flex justify-between">
          <Button variant="outline" onClick={onBack}>
            Back
          </Button>
          <Button onClick={onNext} disabled={selectedSeatIds.length === 0}>
            Next
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function SeatGridLoader({
  tripId,
  selectedSeatIds,
  onToggleSeat,
}: {
  tripId: string;
  selectedSeatIds: string[];
  onToggleSeat: (seatId: string) => void;
}) {
  const { data: seats } = useSuspenseQuery({
    queryKey: getGetTripSeatsQueryKey(tripId),
    queryFn: () => getTripSeats(tripId),
  });

  return (
    <SeatGrid
      seats={seats}
      selectedSeatIds={selectedSeatIds}
      onToggleSeat={onToggleSeat}
    />
  );
}

function SeatGridSkeleton() {
  return (
    <div className="space-y-2">
      {/* 4 horizontal rows of seat placeholders */}
      {Array.from({ length: 4 }).map((_, row) => (
        <div key={row} className="flex gap-1.5">
          {Array.from({ length: 8 }).map((_, col) => (
            <Skeleton
              key={col}
              className="aspect-square min-h-10 min-w-10 flex-1 rounded-md"
            />
          ))}
        </div>
      ))}
    </div>
  );
}
