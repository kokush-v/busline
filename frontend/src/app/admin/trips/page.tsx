"use client";

import { useState, useMemo, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useGetTrips } from "@/generated/api/endpoints/trips/trips";
import type { TripReadPublic } from "@/generated/api/model";
import { TripSortBy } from "@/generated/api/model/tripSortBy";
import { SortOrder } from "@/generated/api/model/sortOrder";
import { useTripsApi } from "@/hooks/use-trips-api";
import {
  TripsHeader,
  TripSearchInput,
  TripsTable,
  DeleteTripDialog,
} from "@/components/trips";
import { AdminPageLayout } from "@/components/admin/admin-page-layout";
import { routes } from "@/lib/routes";

const PAGE_SIZE = 20;

export default function TripsPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [sortBy, setSortBy] = useState<TripSortBy>(TripSortBy.created_at);
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.desc);
  const [deleteTarget, setDeleteTarget] = useState<TripReadPublic | null>(null);

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    setOffset(0);
  }, []);

  const { data, isLoading, isError, refetch } = useGetTrips({
    search: search || undefined,
    limit: PAGE_SIZE,
    offset,
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  const { deleteTrip, isMutating } = useTripsApi();

  const trips = useMemo(() => data?.items ?? [], [data?.items]);
  const total = data?.total ?? 0;

  const handleSortChange = (field: TripSortBy) => {
    if (field === sortBy) {
      setSortOrder((prev) =>
        prev === SortOrder.asc ? SortOrder.desc : SortOrder.asc,
      );
    } else {
      setSortBy(field);
      setSortOrder(SortOrder.asc);
    }
    setOffset(0);
  };

  const handleOffsetChange = (newOffset: number) => {
    setOffset(newOffset);
  };

  const handleEdit = (trip: TripReadPublic) => {
    router.push(routes.admin.tripEdit(trip.id));
  };

  const handleDelete = () => {
    if (!deleteTarget) return;
    deleteTrip(deleteTarget.id, () => {
      setDeleteTarget(null);
    });
  };

  return (
    <AdminPageLayout>
      <TripsHeader onAddTrip={() => router.push(routes.admin.tripNew)} />
      <TripSearchInput value={search} onChange={handleSearchChange} />
      <TripsTable
        trips={trips}
        isLoading={isLoading}
        isError={isError}
        onRetry={refetch}
        search={search}
        onEdit={handleEdit}
        onDelete={setDeleteTarget}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSortChange}
        offset={offset}
        limit={PAGE_SIZE}
        total={total}
        onOffsetChange={handleOffsetChange}
      />

      <DeleteTripDialog
        trip={deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        disabled={isMutating}
      />
    </AdminPageLayout>
  );
}
