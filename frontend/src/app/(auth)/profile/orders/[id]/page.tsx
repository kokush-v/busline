"use client";

import { use } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { AsyncBoundary } from "@/components/ui/error-boundary";
import { Skeleton } from "@/components/ui/skeleton";
import { OrderDetailsPage } from "@/components/profile/order-details-page";

export default function OrderDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const queryClient = useQueryClient();

  return (
    <ProtectedRoute>
      <AsyncBoundary
        fallback={<OrderDetailsSkeleton />}
        onReset={() => queryClient.invalidateQueries()}
        fallbackMessage="Failed to load order."
      >
        <OrderDetailsPage orderId={id} />
      </AsyncBoundary>
    </ProtectedRoute>
  );
}

function OrderDetailsSkeleton() {
  return (
    <div className="mx-auto w-full max-w-[80%] space-y-6 pt-6">
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Order info skeleton */}
        <div className="space-y-4 rounded-xl border p-6">
          <Skeleton className="h-5 w-40" />
          <div className="flex items-center gap-3">
            <Skeleton className="h-5 w-20 rounded-md" />
            <Skeleton className="h-4 w-24" />
          </div>
          <Skeleton className="h-6 w-16" />
        </div>
        {/* Trip route skeleton */}
        <div className="space-y-4 rounded-xl border p-6">
          <Skeleton className="h-5 w-48" />
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Skeleton className="size-5 rounded-full" />
              <Skeleton className="h-4 w-36" />
            </div>
            <div className="flex items-center gap-3">
              <Skeleton className="size-5 rounded-full" />
              <Skeleton className="h-4 w-36" />
            </div>
          </div>
        </div>
      </div>
      {/* Tickets skeleton */}
      <div className="space-y-4 rounded-xl border p-6">
        <Skeleton className="h-5 w-20" />
        <div className="space-y-2">
          <Skeleton className="h-12 w-full rounded-md" />
          <Skeleton className="h-12 w-full rounded-md" />
        </div>
      </div>
    </div>
  );
}
