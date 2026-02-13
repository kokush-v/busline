import { PlusIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";

type BusesHeaderProps = {
  onAddBus: () => void;
};

export function BusesHeader({ onAddBus }: BusesHeaderProps) {
  return (
    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <Text role="h2">Buses</Text>
        <Text role="muted">Manage buses available in the system.</Text>
      </div>
      <Button onClick={onAddBus}>
        <PlusIcon className="size-4" />
        Add Bus
      </Button>
    </div>
  );
}
