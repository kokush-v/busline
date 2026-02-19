import { Skeleton } from "@/components/ui/skeleton";
import { TableCell, TableRow } from "@/components/ui/table";

type SkeletonColumn = {
  skeleton: string;
  cell?: string;
};

type TableSkeletonRowsProps = {
  count: number;
  columns: SkeletonColumn[];
  actions?: number;
};

export function TableSkeletonRows({
  count,
  columns,
  actions = 2,
}: TableSkeletonRowsProps) {
  return Array.from({ length: count }, (_, i) => (
    <TableRow key={i}>
      {columns.map((col, j) => (
        <TableCell key={j} className={col.cell}>
          <Skeleton className={col.skeleton} />
        </TableCell>
      ))}
      {actions > 0 && (
        <TableCell className="text-right">
          <div className="flex justify-end gap-1">
            {Array.from({ length: actions }, (_, k) => (
              <Skeleton key={k} className="size-8 rounded-md" />
            ))}
          </div>
        </TableCell>
      )}
    </TableRow>
  ));
}
