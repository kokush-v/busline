import {
  ArrowUpDown,
  ChevronUp,
  ChevronDown,
  PencilIcon,
  TrashIcon,
} from "lucide-react";
import type { CityRead } from "@/generated/api/model";
import type { CitySortBy } from "@/generated/api/model/citySortBy";
import type { SortOrder } from "@/generated/api/model/sortOrder";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Pagination } from "@/components/ui/pagination";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

type CitiesTableProps = {
  cities: CityRead[];
  isLoading: boolean;
  search: string;
  editingCityId?: string;
  onEdit: (city: CityRead) => void;
  onDelete: (city: CityRead) => void;
  sortBy: CitySortBy;
  sortOrder: SortOrder;
  onSortChange: (field: CitySortBy) => void;
  offset: number;
  limit: number;
  total: number;
  onOffsetChange: (offset: number) => void;
};

function SortableHead({
  label,
  field,
  activeSortBy,
  activeSortOrder,
  onSort,
  className,
}: {
  label: string;
  field: CitySortBy;
  activeSortBy: CitySortBy;
  activeSortOrder: SortOrder;
  onSort: (field: CitySortBy) => void;
  className?: string;
}) {
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

export function CitiesTable({
  cities,
  isLoading,
  search,
  editingCityId,
  onEdit,
  onDelete,
  sortBy,
  sortOrder,
  onSortChange,
  offset,
  limit,
  total,
  onOffsetChange,
}: CitiesTableProps) {
  const skeletonRows = Array.from({ length: limit }, (_, i) => i);

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-md border">
        <Table className="table-fixed">
          <colgroup>
            <col className="w-[35%]" />
            <col className="w-[15%]" />
            <col className="w-[15%]" />
            <col className="w-[20%]" />
            <col className="w-[15%]" />
          </colgroup>
          <TableHeader>
            <TableRow>
              <SortableHead
                label="Name"
                field={"name" as CitySortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <TableHead>Longitude</TableHead>
              <TableHead>Latitude</TableHead>
              <SortableHead
                label="Created At"
                field={"created_at" as CitySortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              skeletonRows.map((i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Skeleton className="h-4 w-32" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-16" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-16" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-24" />
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Skeleton className="size-8 rounded-md" />
                      <Skeleton className="size-8 rounded-md" />
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : cities.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={5}
                  className="text-muted-foreground h-48 text-center"
                >
                  {search
                    ? "No cities found matching your search."
                    : "No cities yet."}
                </TableCell>
              </TableRow>
            ) : (
              cities.map((city) => (
                <TableRow
                  key={city.id}
                  className={cn(
                    "cursor-pointer",
                    editingCityId === city.id && "bg-muted/50",
                  )}
                  onClick={() => onEdit(city)}
                >
                  <TableCell className="font-medium">{city.name}</TableCell>
                  <TableCell>{city.longitude}</TableCell>
                  <TableCell>{city.latitude}</TableCell>
                  <TableCell>
                    {new Date(city.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => onEdit(city)}
                      >
                        <PencilIcon className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => onDelete(city)}
                      >
                        <TrashIcon className="size-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Pagination
        offset={offset}
        limit={limit}
        total={total}
        onPrevious={() => onOffsetChange(Math.max(0, offset - limit))}
        onNext={() => onOffsetChange(offset + limit)}
        onPageChange={(page) => onOffsetChange((page - 1) * limit)}
        isLoading={isLoading}
      />
    </div>
  );
}
