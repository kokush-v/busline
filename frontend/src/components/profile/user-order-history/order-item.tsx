import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Badge } from "@/components/ui/badge";
import { routes } from "@/lib/routes";
import type { OrderStatus } from "@/generated/api/model";

const statusBadgeVariant: Record<
  OrderStatus,
  "success" | "warning" | "destructive"
> = {
  PAID: "success",
  PENDING: "warning",
  PROCESSING: "warning",
  FAILED: "destructive",
  CANCELLED: "destructive",
};

type OrderItemProps = {
  id: string;
  date: string;
  status: OrderStatus;
  total: string;
};

export function OrderItem({ id, date, status, total }: OrderItemProps) {
  const isCancelled = status === "CANCELLED";

  const content = (
    <>
      <div className="text-left">
        <Text className="text-sm font-medium">Order - {id.slice(0, 8)}</Text>
        <Text role="date">{date}</Text>
      </div>
      <div className="flex items-center gap-3">
        <Badge variant={statusBadgeVariant[status]}>{status}</Badge>
        <Text className="text-sm font-semibold">{total}</Text>
        {!isCancelled && (
          <ChevronRight className="text-muted-foreground size-4 shrink-0" />
        )}
      </div>
    </>
  );

  if (isCancelled) {
    return (
      <div className="border-border flex w-full flex-col justify-between gap-2 rounded-lg border px-4 py-3 opacity-60 md:flex-row md:items-center">
        {content}
      </div>
    );
  }

  return (
    <Link
      href={routes.orderDetails(id)}
      className="border-border hover:bg-muted/50 flex w-full flex-col justify-between gap-2 rounded-lg border px-4 py-3 transition-colors md:flex-row md:items-center"
    >
      {content}
    </Link>
  );
}
