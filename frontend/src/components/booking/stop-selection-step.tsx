"use client";

import { useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Combobox } from "@/components/ui/combobox";
import { Label } from "@/components/ui/label";
import { TripStopTimeline } from "@/components/public-trips/trip-stop-timeline";
import type { TripStopReadPublic } from "@/generated/api/model";

type StopSelectionStepProps = {
  stops: TripStopReadPublic[];
  startStopId: string;
  finishStopId: string;
  onStartStopChange: (id: string) => void;
  onFinishStopChange: (id: string) => void;
  onNext: () => void;
};

export function StopSelectionStep({
  stops,
  startStopId,
  finishStopId,
  onStartStopChange,
  onFinishStopChange,
  onNext,
}: StopSelectionStepProps) {
  const sorted = useMemo(
    () => [...stops].sort((a, b) => a.position_index - b.position_index),
    [stops],
  );

  const boardingOptions = sorted.map((ts) => ({
    value: ts.stop.id,
    label: `${ts.stop.name} (${ts.stop.city.name})`,
  }));

  const startIndex = sorted.findIndex((ts) => ts.stop.id === startStopId);

  const alightingOptions = sorted
    .filter((ts) =>
      startStopId
        ? ts.position_index > (sorted[startIndex]?.position_index ?? -1)
        : true,
    )
    .map((ts) => ({
      value: ts.stop.id,
      label: `${ts.stop.name} (${ts.stop.city.name})`,
    }));

  const handleStartChange = (id: string) => {
    onStartStopChange(id);
    // Reset finish if it's no longer valid
    const newStartIdx = sorted.findIndex((ts) => ts.stop.id === id);
    const finishIdx = sorted.findIndex((ts) => ts.stop.id === finishStopId);
    if (finishIdx !== -1 && finishIdx <= newStartIdx) {
      onFinishStopChange("");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Select Your Stops</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label>Boarding Stop</Label>
            <Combobox
              options={boardingOptions}
              value={startStopId}
              onChange={handleStartChange}
              placeholder="Select boarding stop..."
            />
          </div>
          <div className="space-y-2">
            <Label>Alighting Stop</Label>
            <Combobox
              options={alightingOptions}
              value={finishStopId}
              onChange={onFinishStopChange}
              placeholder="Select alighting stop..."
            />
          </div>
        </div>

        <div>
          <p className="text-muted-foreground mb-3 text-sm">Route overview</p>
          <TripStopTimeline stops={stops} />
        </div>

        <div className="flex justify-end">
          <Button onClick={onNext} disabled={!startStopId || !finishStopId}>
            Next
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
