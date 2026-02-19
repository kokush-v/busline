import { CheckIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import type { BookingStep } from "./types";

const steps = [
  { number: 1, label: "Select Stops" },
  { number: 2, label: "Choose Seats" },
  { number: 3, label: "Passenger Details" },
] as const;

type BookingStepIndicatorProps = {
  currentStep: BookingStep;
};

export function BookingStepIndicator({
  currentStep,
}: BookingStepIndicatorProps) {
  const activeNum = currentStep === "success" ? 4 : currentStep;

  return (
    <div className="flex items-center justify-center gap-2">
      {steps.map((step, index) => {
        const isCompleted = activeNum > step.number;
        const isActive = activeNum === step.number;

        return (
          <div key={step.number} className="flex items-center gap-2">
            {index > 0 && (
              <div
                className={cn(
                  "h-px w-8 transition-colors duration-500 sm:w-12",
                  isCompleted || isActive ? "bg-primary" : "bg-muted",
                )}
              />
            )}
            <div className="flex flex-col items-center gap-1">
              <div
                className={cn(
                  "flex size-8 items-center justify-center rounded-full text-sm font-medium transition-all duration-500",
                  isCompleted && "bg-primary text-primary-foreground scale-100",
                  isActive &&
                    "bg-primary text-primary-foreground ring-primary/30 scale-110 ring-4",
                  !isCompleted &&
                    !isActive &&
                    "bg-muted text-muted-foreground scale-100",
                )}
              >
                {isCompleted ? (
                  <CheckIcon className="animate-in zoom-in-0 size-4 duration-300" />
                ) : (
                  step.number
                )}
              </div>
              <span
                className={cn(
                  "text-xs whitespace-nowrap",
                  isActive
                    ? "text-foreground font-medium"
                    : "text-muted-foreground",
                )}
              >
                {step.label}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
