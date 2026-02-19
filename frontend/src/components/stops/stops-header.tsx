import { PlusIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";

type StopsHeaderProps = {
  onAddStop: () => void;
};

export function StopsHeader({ onAddStop }: StopsHeaderProps) {
  return (
    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <Text role="h2">Stops</Text>
        <Text role="muted">Manage bus stops available in the system.</Text>
      </div>
      <Button onClick={onAddStop}>
        <PlusIcon className="size-4" />
        Add Stop
      </Button>
    </div>
  );
}
