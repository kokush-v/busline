import { ArrowUpDown, ChevronUp, ChevronDown } from "lucide-react";
import type { SortOrder } from "@/generated/api/model/sortOrder";
import { TableHead } from "@/components/ui/table";

type SortableHeadProps<T extends string> = {
  label: string;
  field: T;
  activeSortBy: T;
  activeSortOrder: SortOrder;
  onSort: (field: T) => void;
  className?: string;
};

export function SortableHead<T extends string>({
  label,
  field,
  activeSortBy,
  activeSortOrder,
  onSort,
  className,
}: SortableHeadProps<T>) {
  const isActive = field === activeSortBy;
  const Icon = isActive
    ? activeSortOrder === "asc"
      ? ChevronUp
      : ChevronDown
    : ArrowUpDown;

  return (
    <TableHead className={className}>
      <button
        type="button"
        className="hover:text-foreground flex items-center gap-1"
        onClick={() => onSort(field)}
      >
        {label}
        <Icon className="size-4" />
      </button>
    </TableHead>
  );
}
