import { PlusIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";

type CitiesHeaderProps = {
  onAddCity: () => void;
};

export function CitiesHeader({ onAddCity }: CitiesHeaderProps) {
  return (
    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
      <div>
        <Text role="h2">Cities</Text>
        <Text role="muted">Manage cities available in the system.</Text>
      </div>
      <Button onClick={onAddCity}>
        <PlusIcon className="size-4" />
        Add City
      </Button>
    </div>
  );
}
