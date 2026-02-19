import { Input } from "@/components/ui/input";

type ColorPickerProps = {
  id?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  maxLength?: number;
};

export function ColorPicker({
  id,
  value,
  onChange,
  placeholder = "#FFCC00",
  required,
  maxLength = 50,
}: ColorPickerProps) {
  return (
    <div className="flex gap-2">
      <input
        type="color"
        value={value || "#000000"}
        onChange={(e) => onChange(e.target.value)}
        className="border-input h-9 w-9 shrink-0 cursor-pointer rounded-md border p-0.5"
      />
      <Input
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        maxLength={maxLength}
        required={required}
      />
    </div>
  );
}
