import { XIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

type TripDateFilterProps = {
  departureDateFrom: string;
  departureDateTo: string;
  onDepartureDateFromChange: (value: string) => void;
  onDepartureDateToChange: (value: string) => void;
};

export function TripDateFilter({
  departureDateFrom,
  departureDateTo,
  onDepartureDateFromChange,
  onDepartureDateToChange,
}: TripDateFilterProps) {
  const hasValue = departureDateFrom || departureDateTo;

  return (
    <div className="flex items-end gap-2">
      <div className="space-y-1">
        <Label htmlFor="departure-from" className="text-xs">
          Departure from
        </Label>
        <Input
          id="departure-from"
          type="date"
          value={departureDateFrom}
          onChange={(e) => onDepartureDateFromChange(e.target.value)}
          className="w-36"
        />
      </div>
      <div className="space-y-1">
        <Label htmlFor="departure-to" className="text-xs">
          Departure to
        </Label>
        <Input
          id="departure-to"
          type="date"
          value={departureDateTo}
          onChange={(e) => onDepartureDateToChange(e.target.value)}
          className="w-36"
        />
      </div>
      {hasValue && (
        <Button
          variant="ghost"
          size="icon"
          className="size-9"
          onClick={() => {
            onDepartureDateFromChange("");
            onDepartureDateToChange("");
          }}
        >
          <XIcon className="size-4" />
        </Button>
      )}
    </div>
  );
}
