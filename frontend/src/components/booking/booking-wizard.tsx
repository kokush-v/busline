"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { useSuspenseQuery } from "@tanstack/react-query";
import { ArrowLeftIcon, ArrowRightIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { routes } from "@/lib/routes";
import {
  getTripPublic,
  getGetTripPublicQueryKey,
  getGetTripSeatsQueryKey,
  getTripSeats,
} from "@/generated/api/endpoints/trips/trips";
import type { ReserveSeatResponse, SeatRead } from "@/generated/api/model";
import { BookingStepIndicator } from "./booking-step-indicator";
import { StopSelectionStep } from "./stop-selection-step";
import { SeatSelectionStep } from "./seat-selection-step";
import { PassengerInfoStep } from "./passenger-info-step";
import { BookingSuccess } from "./booking-success";
import type { BookingStep, BookingSuccessData } from "./types";

type BookingWizardProps = {
  tripId: string;
};

export function BookingWizard({ tripId }: BookingWizardProps) {
  const { data: trip } = useSuspenseQuery({
    queryKey: getGetTripPublicQueryKey(tripId),
    queryFn: () => getTripPublic(tripId),
  });

  const [step, setStep] = useState<BookingStep>(1);
  const [direction, setDirection] = useState<"forward" | "back">("forward");
  const [animKey, setAnimKey] = useState(0);
  const [startStopId, setStartStopId] = useState("");
  const [finishStopId, setFinishStopId] = useState("");

  const goTo = (next: BookingStep) => {
    const numCurrent = step === "success" ? 4 : step;
    const numNext = next === "success" ? 4 : next;
    setDirection(numNext >= numCurrent ? "forward" : "back");
    setAnimKey((k) => k + 1);
    setStep(next);
  };
  const [selectedSeatIds, setSelectedSeatIds] = useState<string[]>([]);
  const [order, setOrder] = useState<BookingSuccessData | null>(null);

  // Pre-fetch seats data for step 2
  const { data: seats } = useSuspenseQuery({
    queryKey: getGetTripSeatsQueryKey(tripId),
    queryFn: () => getTripSeats(tripId),
  });

  const stops = trip.trip_stops;
  const sorted = useMemo(
    () => [...stops].sort((a, b) => a.position_index - b.position_index),
    [stops],
  );
  const fromCity = sorted[0]?.stop.city.name ?? "—";
  const toCity = sorted[sorted.length - 1]?.stop.city.name ?? "—";

  const handleToggleSeat = (seatId: string) => {
    setSelectedSeatIds((prev) =>
      prev.includes(seatId)
        ? prev.filter((id) => id !== seatId)
        : [...prev, seatId],
    );
  };

  const selectedSeats = useMemo(
    () =>
      seats
        .filter((s: SeatRead) => selectedSeatIds.includes(s.id))
        .map((s: SeatRead) => ({ id: s.id, position_index: s.position_index })),
    [seats, selectedSeatIds],
  );

  const handleSuccess = (response: ReserveSeatResponse) => {
    setOrder(response);
    goTo("success");
  };

  if (step === "success" && order) {
    return (
      <div className="animate-in fade-in-0 zoom-in-95 space-y-6 duration-500">
        <BookingStepIndicator currentStep="success" />
        <BookingSuccess order={order} tripId={tripId} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <Button asChild variant="ghost" size="sm" className="gap-1">
            <Link href={routes.tripDetails(tripId)}>
              <ArrowLeftIcon className="size-4" />
              Back to trip
            </Link>
          </Button>
          <span className="text-muted-foreground text-sm">
            {trip.price_per_seat} UAH per seat
          </span>
        </div>

        <div className="mt-3 flex flex-wrap items-center justify-center gap-2">
          <h1 className="flex items-center gap-2 text-lg font-semibold">
            {fromCity}
            <ArrowRightIcon className="size-4 shrink-0" />
            {toCity}
          </h1>
        </div>

        <div className="mt-4">
          <BookingStepIndicator currentStep={step} />
        </div>
      </Card>

      <div
        key={animKey}
        className={cn(
          "animate-in fade-in-0 duration-300",
          direction === "forward"
            ? "slide-in-from-right-4"
            : "slide-in-from-left-4",
        )}
      >
        {step === 1 && (
          <StopSelectionStep
            stops={stops}
            startStopId={startStopId}
            finishStopId={finishStopId}
            onStartStopChange={setStartStopId}
            onFinishStopChange={setFinishStopId}
            onNext={() => goTo(2)}
          />
        )}

        {step === 2 && (
          <SeatSelectionStep
            tripId={tripId}
            selectedSeatIds={selectedSeatIds}
            onToggleSeat={handleToggleSeat}
            onBack={() => goTo(1)}
            onNext={() => goTo(3)}
          />
        )}

        {step === 3 && (
          <PassengerInfoStep
            tripId={tripId}
            startStopId={startStopId}
            finishStopId={finishStopId}
            selectedSeats={selectedSeats}
            pricePerSeat={trip.price_per_seat}
            onBack={() => goTo(2)}
            onSuccess={handleSuccess}
          />
        )}
      </div>
    </div>
  );
}
