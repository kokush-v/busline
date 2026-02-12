"use client";

import { useMemo } from "react";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Text } from "@/components/ui/text";
import { Pagination } from "@/components/ui/pagination";
import { getUserOrders } from "@/generated/api/endpoints/orders/orders";
import { OrderItem } from "./order-item";
import { ProfileOrderFilterEnum } from "@/generated/api/model";

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
  });

  const orders = useMemo(() => {
    if (!data?.items) return [];

    return data.items.map((order) => ({
      id: order.id,
      date: order.created_at,
      status: order.status,
      total: `₴${order.total_price || 0}`,
    }));
  }, [data?.items]);

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
