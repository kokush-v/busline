import { PencilIcon, TrashIcon, RefreshCwIcon, ImageIcon } from "lucide-react";
import type { BusRead } from "@/generated/api/model";
import type { BusSortBy } from "@/generated/api/model/busSortBy";
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
import { LoadingImage } from "@/components/ui/loading-image";
import { SortableHead } from "@/components/ui/sortable-head";

type BusesTableProps = {
  buses: BusRead[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  search: string;
  editingBusId?: string;
  onEdit: (bus: BusRead) => void;
  onDelete: (bus: BusRead) => void;
  sortBy: BusSortBy;
  sortOrder: SortOrder;
  onSortChange: (field: BusSortBy) => void;
  offset: number;
  limit: number;
  total: number;
  onOffsetChange: (offset: number) => void;
};

export function BusesTable({
  buses,
  isLoading,
  isError,
  onRetry,
  search,
  editingBusId,
  onEdit,
  onDelete,
  sortBy,
  sortOrder,
  onSortChange,
  offset,
  limit,
  total,
  onOffsetChange,
}: BusesTableProps) {
  const skeletonRows = Array.from({ length: limit }, (_, i) => i);

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-md border">
        <Table>
          <colgroup>
            <col className="w-18" />
            <col />
            <col />
            <col />
            <col />
            <col className="w-28" />
          </colgroup>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12" />
              <SortableHead
                label="Number Plate"
                field={"number_plate" as BusSortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <SortableHead
                label="Color"
                field={"color" as BusSortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <SortableHead
                label="Seats"
                field={"seats_quantity" as BusSortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <SortableHead
                label="Created At"
                field={"created_at" as BusSortBy}
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
                  <TableCell className="px-2">
                    <Skeleton className="size-14 rounded" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-24" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-20" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-12" />
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
                      Failed to load buses.
                    </span>
                    <Button variant="outline" size="sm" onClick={onRetry}>
                      <RefreshCwIcon className="size-4" />
                      Retry
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ) : buses.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-muted-foreground h-48 text-center"
                >
                  {search
                    ? "No buses found matching your search."
                    : "No buses yet."}
                </TableCell>
              </TableRow>
            ) : (
              buses.map((bus) => (
                <TableRow
                  key={bus.id}
                  className={cn(
                    "cursor-pointer",
                    editingBusId === bus.id && "bg-muted/50",
                  )}
                  onClick={() => onEdit(bus)}
                >
                  <TableCell className="w-18 px-2">
                    <LoadingImage
                      src={bus.thumbnail_url ?? undefined}
                      alt={bus.number_plate}
                      className="size-14 rounded"
                      fallback={
                        <div className="bg-muted flex size-14 items-center justify-center rounded">
                          <ImageIcon className="text-muted-foreground size-4" />
                        </div>
                      }
                    />
                  </TableCell>
                  <TableCell className="font-medium">
                    {bus.number_plate}
                  </TableCell>
                  <TableCell>{bus.color}</TableCell>
                  <TableCell>{bus.seats_quantity}</TableCell>
                  <TableCell>
                    {new Date(bus.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={() => onEdit(bus)}
                      >
                        <PencilIcon className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(bus);
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
