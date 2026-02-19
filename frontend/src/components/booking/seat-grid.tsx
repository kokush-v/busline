"use client";

import { cn } from "@/lib/utils";
import type { SeatRead } from "@/generated/api/model";
import { SeatStatus } from "@/generated/api/model";

type SeatGridProps = {
  seats: SeatRead[];
  selectedSeatIds: string[];
  onToggleSeat: (seatId: string) => void;
};

export function SeatGrid({
  seats,
  selectedSeatIds,
  onToggleSeat,
}: SeatGridProps) {
  const sorted = [...seats].sort((a, b) => a.position_index - b.position_index);

  const hasAisle = sorted.length > 20;
  const seatsPerCol = hasAisle ? 4 : 2;

  // Build columns: 4 seats (2+aisle+2) for large buses, 2 seats for small
  const columns: (SeatRead | null)[][] = [];
  for (let i = 0; i < sorted.length; i += seatsPerCol) {
    const col: (SeatRead | null)[] = [];
    for (let j = 0; j < seatsPerCol; j++) {
      col.push(sorted[i + j] ?? null);
    }
    columns.push(col);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-muted-foreground shrink-0 text-xs">Front</span>
        <div className="bg-border h-px flex-1" />
        <span className="text-muted-foreground shrink-0 text-xs">Back</span>
      </div>

      {/* Horizontal scrollable seat grid */}
      <div className="flex justify-center overflow-x-auto">
        <div
          className={cn(
            "grid gap-1.5",
            hasAisle
              ? "grid-rows-[1fr_0.5fr_1fr_1fr_0.5fr_1fr]"
              : "grid-rows-2",
          )}
          style={{
            gridTemplateColumns: `repeat(${columns.length}, minmax(1.75rem, 60px))`,
          }}
        >
          {columns.map((col, colIdx) =>
            col.map((seat, rowIdx) => {
              const gridRow = hasAisle
                ? rowIdx < 2
                  ? rowIdx + 1
                  : rowIdx + 2
                : rowIdx + 1;
              return (
                <div
                  key={`${colIdx}-${rowIdx}`}
                  style={{ gridColumn: colIdx + 1, gridRow }}
                >
                  {seat ? (
                    <SeatButton
                      seat={seat}
                      isSelected={selectedSeatIds.includes(seat.id)}
                      onToggle={() => onToggleSeat(seat.id)}
                    />
                  ) : (
                    <div className="aspect-square min-h-7 min-w-7" />
                  )}
                </div>
              );
            }),
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-4 pt-2">
        <LegendItem
          className="border-border bg-background border"
          label="Available"
        />
        <LegendItem className="bg-primary" label="Selected" />
        <LegendItem className="bg-amber-400/80" label="Locked" />
        <LegendItem className="bg-muted" label="Sold" />
      </div>
    </div>
  );
}

function SeatButton({
  seat,
  isSelected,
  onToggle,
}: {
  seat: SeatRead;
  isSelected: boolean;
  onToggle: () => void;
}) {
  const isFree = seat.status === SeatStatus.FREE;
  const isLocked = seat.status === SeatStatus.LOCKED;
  const isSold = seat.status === SeatStatus.SOLD;

  return (
    <button
      type="button"
      disabled={!isFree}
      onClick={onToggle}
      className={cn(
        "flex aspect-square min-h-7 w-full min-w-7 items-center justify-center rounded-md text-xs font-medium transition-colors",
        isFree &&
          !isSelected &&
          "border-border hover:border-primary hover:text-primary bg-background cursor-pointer border",
        isFree && isSelected && "bg-primary text-primary-foreground",
        isLocked && "cursor-not-allowed bg-amber-400/80 text-amber-900",
        isSold && "bg-muted text-muted-foreground cursor-not-allowed",
      )}
      title={`Seat ${seat.position_index} — ${seat.status}`}
    >
      {seat.position_index}
    </button>
  );
}

function LegendItem({
  className,
  label,
}: {
  className: string;
  label: string;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <div className={cn("size-4 rounded-sm", className)} />
      <span className="text-muted-foreground text-xs">{label}</span>
    </div>
  );
}
