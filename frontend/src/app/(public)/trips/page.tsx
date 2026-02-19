"use client";

import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { PageContainer } from "@/components/ui/page-container";
import { AsyncBoundary } from "@/components/ui/error-boundary";
import {
  TripCardList,
  TripCardListSkeleton,
  TripFilters,
} from "@/components/public-trips";
import { TripSortBy, SortOrder } from "@/generated/api/model";

const PAGE_SIZE = 12;

export default function TripsPage() {
  const queryClient = useQueryClient();
  const [offset, setOffset] = useState(0);
  const [fromStopId, setFromStopId] = useState("");
  const [toStopId, setToStopId] = useState("");
  const [departureDateFrom, setDepartureDateFrom] = useState("");
  const [departureDateTo, setDepartureDateTo] = useState("");
  const [sortBy, setSortBy] = useState<TripSortBy>(TripSortBy.departure_time);
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.asc);
  const [retryKey, setRetryKey] = useState(0);

  const resetOffset = () => setOffset(0);

  const params = {
    limit: PAGE_SIZE,
    offset,
    sort_by: sortBy,
    sort_order: sortOrder,
    from_stop_id: fromStopId || undefined,
    to_stop_id: toStopId || undefined,
    departure_date_from: departureDateFrom || undefined,
    departure_date_to: departureDateTo || undefined,
  };

  const suspenseKey = JSON.stringify({ ...params, retryKey });

  return (
    <PageContainer centered={false}>
      <div className="mx-auto max-w-6xl space-y-6">
        <h1 className="text-2xl font-semibold tracking-tight">
          Available Trips
        </h1>

        <TripFilters
          fromStopId={fromStopId}
          toStopId={toStopId}
          departureDateFrom={departureDateFrom}
          departureDateTo={departureDateTo}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onFromStopChange={(v) => {
            setFromStopId(v);
            resetOffset();
          }}
          onToStopChange={(v) => {
            setToStopId(v);
            resetOffset();
          }}
          onDepartureDateFromChange={(v) => {
            setDepartureDateFrom(v);
            resetOffset();
          }}
          onDepartureDateToChange={(v) => {
            setDepartureDateTo(v);
            resetOffset();
          }}
          onSortChange={(newSortBy, newSortOrder) => {
            setSortBy(newSortBy);
            setSortOrder(newSortOrder);
            resetOffset();
          }}
        />

        <AsyncBoundary
          onReset={() => {
            queryClient.removeQueries({ queryKey: ["/trips/list"] });
            setRetryKey((k) => k + 1);
          }}
          fallbackMessage="Unable to load trips."
          suspenseKey={suspenseKey}
          fallback={<TripCardListSkeleton />}
        >
          <TripCardList params={params} onOffsetChange={setOffset} />
        </AsyncBoundary>
      </div>
    </PageContainer>
  );
}
