"use client";

import { useEffect, useMemo, useState } from "react";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Text } from "@/components/ui/text";
import { Spinner } from "@/components/ui/spinner";
import { Pagination } from "@/components/ui/pagination";
import { useGetUserOrders } from "@/generated/api/endpoints/orders/orders";
import { OrderStatus } from "@/generated/api/model/orderStatus";

export function UserOrderHistory() {
  const [status, setStatus] = useState<OrderStatus>(OrderStatus.PENDING);
  const [offset, setOffset] = useState(0);
  const limit = 10;
  const selectedStatuses = [status];

  useEffect(() => {
    setOffset(0);
  }, [status]);

  const { data, isLoading } = useGetUserOrders(selectedStatuses, {
    limit,
    offset,
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
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <Text role="h3">Order history</Text>
          <Text role="muted">Search and filter your orders</Text>
        </div>

        <Tabs
          value={status}
          onValueChange={(value) => setStatus(value as OrderStatus)}
        >
          <TabsList>
            {Object.values(OrderStatus).map((value) => (
              <TabsTrigger key={value} value={value}>
                {value}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>
      <Separator />
      <div className="space-y-3">
        {isLoading ? (
          <div className="text-muted-foreground flex items-center gap-2 text-sm">
            <Spinner />
            Loading orders…
          </div>
        ) : orders.length === 0 ? (
          <Text role="muted">No orders for the current filter.</Text>
        ) : (
          orders.map((order) => (
            <div
              key={order.id}
              className="border-border flex flex-col justify-between gap-2 rounded-lg border px-4 py-3 md:flex-row md:items-center"
            >
              <div>
                <p className="text-sm font-medium">
                  Order - {order.id.slice(0, 8)}
                </p>
                <Text role="date">{order.date}</Text>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-muted-foreground text-xs">
                  {order.status}
                </span>
                <span className="text-sm font-semibold">{order.total}</span>
              </div>
            </div>
          ))
        )}
        <Pagination
          offset={offset}
          limit={limit}
          total={data?.total || 0}
          onPrevious={() => setOffset((prev) => Math.max(0, prev - limit))}
          onNext={() => setOffset((prev) => prev + limit)}
          onPageChange={(page) => setOffset((page - 1) * limit)}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
