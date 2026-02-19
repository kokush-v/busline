import { MapPinIcon } from "lucide-react";
import type { TripStopReadPublic } from "@/generated/api/model";

type TripStopTimelineProps = {
  stops: TripStopReadPublic[];
};

function formatTime(iso: string) {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function TripStopTimeline({ stops }: TripStopTimelineProps) {
  const sorted = [...stops].sort((a, b) => a.position_index - b.position_index);

  return (
    <div className="relative space-y-0">
      {sorted.map((ts, index) => {
        const isFirst = index === 0;
        const isLast = index === sorted.length - 1;

        return (
          <div key={ts.stop.id} className="relative flex gap-4 pb-6 last:pb-0">
            {/* Vertical line */}
            {!isLast && (
              <div className="bg-border absolute top-5 left-[11px] h-[calc(100%-12px)] w-px" />
            )}

            {/* Dot */}
            <div className="relative z-10 mt-1 flex size-6 shrink-0 items-center justify-center">
              <MapPinIcon
                className={`size-5 ${isFirst || isLast ? "text-primary" : "text-muted-foreground"}`}
              />
            </div>

            {/* Content */}
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium">
                {ts.stop.name}{" "}
                <span className="text-muted-foreground font-normal">
                  ({ts.stop.city.name})
                </span>
              </p>
              <div className="text-muted-foreground mt-0.5 flex flex-wrap gap-x-4 text-xs">
                {isFirst ? (
                  <span>Departs: {formatTime(ts.departure_time)}</span>
                ) : isLast ? (
                  <span>Arrives: {formatTime(ts.arrival_time)}</span>
                ) : (
                  <>
                    <span>Arr: {formatTime(ts.arrival_time)}</span>
                    <span>Dep: {formatTime(ts.departure_time)}</span>
                  </>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
