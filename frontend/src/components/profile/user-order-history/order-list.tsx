"use client";

import { useSuspenseQuery } from "@tanstack/react-query";
import { Text } from "@/components/ui/text";
import { Pagination } from "@/components/ui/pagination";
import { getUserOrders } from "@/generated/api/endpoints/orders/orders";
import { OrderItem } from "./order-item";
import type {
  ProfileOrderFilterEnum,
  OrderStatus,
} from "@/generated/api/model";

type OrderListProps = {
  status: ProfileOrderFilterEnum | undefined;
  offset: number;
  limit: number;
  onOffsetChange: (offset: number) => void;
};

export function OrderList({
  status,
  offset,
  limit,
  onOffsetChange,
}: OrderListProps) {
  const { data } = useSuspenseQuery({
    queryKey: ["user-orders", status, offset, limit],
    queryFn: () =>
      getUserOrders({
        limit,
        offset,
        filter: status,
      }),
    refetchInterval: 5000,
  });

  const orders = (data.items ?? []).map((order) => ({
    id: order.id,
    date: order.created_at,
    status: order.status as OrderStatus,
    total: `₴${order.total_price || 0}`,
  }));

  return (
    <div className="space-y-3">
      {orders.length === 0 ? (
        <Text role="muted">No orders for the current filter.</Text>
      ) : (
        orders.map((order) => (
          <OrderItem
            key={order.id}
            id={order.id}
            date={order.date}
            status={order.status}
            total={order.total}
          />
        ))
      )}
      <Pagination
        offset={offset}
        limit={limit}
        total={data?.total || 0}
        onPrevious={() => onOffsetChange(Math.max(0, offset - limit))}
        onNext={() => onOffsetChange(offset + limit)}
        onPageChange={(page) => onOffsetChange((page - 1) * limit)}
      />
    </div>
  );
}
