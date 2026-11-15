import { PencilIcon, TrashIcon, RefreshCwIcon } from "lucide-react";
import type { UserRead } from "@/generated/api/model";
import type { UserSortBy } from "@/generated/api/model/userSortBy";
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
import { cn } from "@/lib/utils";
import { SortableHead } from "@/components/ui/sortable-head";

type UsersTableProps = {
  users: UserRead[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  search: string;
  editingUserId?: string;
  onEdit: (user: UserRead) => void;
  onDelete: (user: UserRead) => void;
  sortBy: UserSortBy;
  sortOrder: SortOrder;
  onSortChange: (field: UserSortBy) => void;
  offset: number;
  limit: number;
  total: number;
  onOffsetChange: (offset: number) => void;
};

const colCount = 7;

export function UsersTable({
  users,
  isLoading,
  isError,
  onRetry,
  search,
  editingUserId,
  onEdit,
  onDelete,
  sortBy,
  sortOrder,
  onSortChange,
  offset,
  limit,
  total,
  onOffsetChange,
}: UsersTableProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-md border">
        <Table className="table-fixed">
          <colgroup>
            <col className="w-[22%]" />
            <col className="w-[16%]" />
            <col className="w-[14%]" />
            <col className="w-[9%]" />
            <col className="w-[9%]" />
            <col className="w-[18%]" />
            <col className="w-[12%]" />
          </colgroup>
          <TableHeader>
            <TableRow>
              <SortableHead
                label="Email"
                field={"email" as UserSortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <SortableHead
                label="Name"
                field={"name" as UserSortBy}
                activeSortBy={sortBy}
                activeSortOrder={sortOrder}
                onSort={onSortChange}
              />
              <TableHead>Phone</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Active</TableHead>
              <SortableHead
                label="Created At"
                field={"created_at" as UserSortBy}
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
                  { skeleton: "h-4 w-36" },
                  { skeleton: "h-4 w-24" },
                  { skeleton: "h-4 w-24" },
                  { skeleton: "h-4 w-14" },
                  { skeleton: "h-4 w-10" },
                  { skeleton: "h-4 w-24" },
                ]}
              />
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={colCount} className="h-48 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-muted-foreground text-sm">
                      Failed to load users.
                    </span>
                    <Button variant="outline" size="sm" onClick={onRetry}>
                      <RefreshCwIcon className="size-4" />
                      Retry
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ) : users.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={colCount}
                  className="text-muted-foreground h-48 text-center"
                >
                  {search
                    ? "No users found matching your search."
                    : "No users yet."}
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow
                  key={user.id}
                  className={cn(
                    "cursor-pointer",
                    editingUserId === user.id && "bg-muted/50",
                  )}
                  onClick={() => onEdit(user)}
                >
                  <TableCell className="font-medium">{user.email}</TableCell>
                  <TableCell>{user.name ?? "—"}</TableCell>
                  <TableCell>{user.phone_number ?? "—"}</TableCell>
                  <TableCell>{user.role}</TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                        user.is_active
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
                      )}
                    >
                      {user.is_active ? "Yes" : "No"}
                    </span>
                  </TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onEdit(user);
                        }}
                      >
                        <PencilIcon className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(user);
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
