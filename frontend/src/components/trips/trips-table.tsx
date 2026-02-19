import { PencilIcon, TrashIcon, RefreshCwIcon } from "lucide-react";
import type { TripReadAdmin } from "@/generated/api/model";
import type { TripAdminSortBy } from "@/generated/api/model/tripAdminSortBy";
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
import { TableSkeletonRows } from "@/components/ui/table-skeleton-rows";
import { SortableHead } from "@/components/ui/sortable-head";

type TripsTableProps = {
  trips: TripReadAdmin[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  search: string;
  onEdit: (trip: TripReadAdmin) => void;
  onDelete: (trip: TripReadAdmin) => void;
  sortBy: TripAdminSortBy;
  sortOrder: SortOrder;
  onSortChange: (field: TripAdminSortBy) => void;
  offset: number;
  limit: number;
  total: number;
  onOffsetChange: (offset: number) => void;
};

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "short",
    timeStyle: "short",
  });
}

export function TripsTable({
  trips,
  isLoading,
  isError,
  onRetry,
  search,
  onEdit,
  onDelete,
  sortBy,
  sortOrder,
  onSortChange,
  offset,
  limit,
  total,
  onOffsetChange,
}: TripsTableProps) {
  const colCount = 6;

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <SortableHead
                label="Price / seat"
                field={"price" as TripAdminSortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <SortableHead
                label="Seats left"
                field={"seats_left" as TripAdminSortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <TableHead>Stops</TableHead>
              <TableHead>First departure</TableHead>
              <SortableHead
                label="Created at"
                field={"created_at" as TripAdminSortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableSkeletonRows
                count={limit}
                columns={[
                  { skeleton: "h-4 w-16" },
                  { skeleton: "h-4 w-12" },
                  { skeleton: "h-4 w-8" },
                  { skeleton: "h-4 w-28" },
                  { skeleton: "h-4 w-24" },
                  { skeleton: "h-4 w-16" },
                ]}
              />
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={colCount} className="h-48 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-muted-foreground text-sm">
                      Failed to load trips.
                    </span>
                    <Button variant="outline" size="sm" onClick={onRetry}>
                      <RefreshCwIcon className="size-4" />
                      Retry
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ) : trips.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={colCount}
                  className="text-muted-foreground h-48 text-center"
                >
                  {search
                    ? "No trips found matching your search."
                    : "No trips yet."}
                </TableCell>
              </TableRow>
            ) : (
              trips.map((trip) => {
                const sortedStops = [...trip.trip_stops].sort(
                  (a, b) => a.position_index - b.position_index,
                );
                const firstDeparture = sortedStops[0]?.departure_time;

                return (
                  <TableRow
                    key={trip.id}
                    className="cursor-pointer"
                    onClick={() => onEdit(trip)}
                  >
                    <TableCell className="font-medium">
                      ${trip.price_per_seat.toFixed(2)}
                    </TableCell>
                    <TableCell>{trip.seats_left}</TableCell>
                    <TableCell>{trip.trip_stops.length}</TableCell>
                    <TableCell>
                      {firstDeparture ? formatDateTime(firstDeparture) : "—"}
                    </TableCell>
                    <TableCell>
                      {new Date(trip.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onEdit(trip);
                          }}
                        >
                          <PencilIcon className="size-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDelete(trip);
                          }}
                        >
                          <TrashIcon className="size-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })
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
