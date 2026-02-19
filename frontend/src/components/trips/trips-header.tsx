import { PlusIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";

type TripsHeaderProps = {
  onAddTrip: () => void;
};

export function TripsHeader({ onAddTrip }: TripsHeaderProps) {
  return (
    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <Text role="h2">Trips</Text>
        <Text role="muted">Manage trips and their routes.</Text>
      </div>
      <Button onClick={onAddTrip}>
        <PlusIcon className="size-4" />
        Add Trip
      </Button>
    </div>
  );
}
