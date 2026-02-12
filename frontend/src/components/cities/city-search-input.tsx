import { SearchIcon } from "lucide-react";
import { Input } from "@/components/ui/input";

type CitySearchInputProps = {
  value: string;
  onChange: (value: string) => void;
};

export function CitySearchInput({ value, onChange }: CitySearchInputProps) {
  return (
    <div className="relative max-w-sm">
      <SearchIcon className="text-muted-foreground absolute top-1/2 left-3 size-4 -translate-y-1/2" />
      <Input
        placeholder="Search cities..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pl-9"
      />
    </div>
  );
}
