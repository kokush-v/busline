import { SearchIcon } from "lucide-react";
import { Input } from "@/components/ui/input";

type BusSearchInputProps = {
  value: string;
  onChange: (value: string) => void;
};

export function BusSearchInput({ value, onChange }: BusSearchInputProps) {
  return (
    <div className="relative max-w-sm">
      <SearchIcon className="text-muted-foreground absolute top-1/2 left-3 size-4 -translate-y-1/2" />
      <Input
        placeholder="Search buses..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pl-9"
      />
    </div>
  );
}
