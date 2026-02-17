import {
  ArrowUpDown,
  ChevronUp,
  ChevronDown,
  PencilIcon,
  TrashIcon,
  RefreshCwIcon,
} from "lucide-react";
import type { StopRead } from "@/generated/api/model";
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

type StopsTableProps = {
  stops: StopRead[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  search: string;
  editingStopId?: string;
  onEdit: (stop: StopRead) => void;
  onDelete: (stop: StopRead) => void;
  sortOrder: SortOrder;
  onSortToggle: () => void;
  offset: number;
  limit: number;
  total: number;
  onOffsetChange: (offset: number) => void;
  cityNameMap: Record<string, string>;
};

export function StopsTable({
  stops,
  isLoading,
  isError,
  onRetry,
  search,
  editingStopId,
  onEdit,
  onDelete,
  sortOrder,
  onSortToggle,
  offset,
  limit,
  total,
  onOffsetChange,
  cityNameMap,
}: StopsTableProps) {
  const skeletonRows = Array.from({ length: limit }, (_, i) => i);

  const SortIcon =
    sortOrder === "asc"
      ? ChevronUp
      : sortOrder === "desc"
        ? ChevronDown
        : ArrowUpDown;

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-md border">
        <Table className="table-fixed">
          <colgroup>
            <col className="w-[25%]" />
            <col className="w-[20%]" />
            <col className="w-[12%]" />
            <col className="w-[12%]" />
            <col className="w-[18%]" />
            <col className="w-[13%]" />
          </colgroup>
          <TableHeader>
            <TableRow>
              <TableHead>
                <button
                  type="button"
                  className="hover:text-foreground flex items-center gap-1"
                  onClick={onSortToggle}
                >
                  Name
                  <SortIcon className="size-4" />
                </button>
              </TableHead>
              <TableHead>City</TableHead>
              <TableHead>Latitude</TableHead>
              <TableHead>Longitude</TableHead>
              <TableHead>Created At</TableHead>
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
                    <Skeleton className="h-4 w-24" />
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
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={6} className="h-48 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-muted-foreground text-sm">
                      Failed to load stops.
                    </span>
                    <Button variant="outline" size="sm" onClick={onRetry}>
                      <RefreshCwIcon className="size-4" />
                      Retry
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ) : stops.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-muted-foreground h-48 text-center"
                >
                  {search
                    ? "No stops found matching your search."
                    : "No stops yet."}
                </TableCell>
              </TableRow>
            ) : (
              stops.map((stop) => (
                <TableRow
                  key={stop.id}
                  className={cn(
                    "cursor-pointer",
                    editingStopId === stop.id && "bg-muted/50",
                  )}
                  onClick={() => onEdit(stop)}
                >
                  <TableCell className="font-medium">{stop.name}</TableCell>
                  <TableCell>
                    {cityNameMap[stop.city_id] ?? stop.city_id}
                  </TableCell>
                  <TableCell>{stop.latitude}</TableCell>
                  <TableCell>{stop.longitude}</TableCell>
                  <TableCell>
                    {new Date(stop.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onEdit(stop);
                        }}
                      >
                        <PencilIcon className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(stop);
                        }}
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
