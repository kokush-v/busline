"use client";

import { useState, useMemo, useCallback } from "react";
import { useGetStops } from "@/generated/api/endpoints/stops/stops";
import { useGetSearchCities } from "@/generated/api/endpoints/cities/cities";
import type { StopRead } from "@/generated/api/model";
import { SortOrder } from "@/generated/api/model/sortOrder";
import { useStopsApi } from "@/hooks/use-stops-api";
import {
  StopsHeader,
  StopSearchInput,
  StopsTable,
  StopFormPanel,
  DeleteStopDialog,
} from "@/components/stops";
import { AdminPageLayout } from "@/components/admin/admin-page-layout";

const PAGE_SIZE = 20;

export default function StopsPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.asc);
  const [deleteTarget, setDeleteTarget] = useState<StopRead | null>(null);
  const [editingStopId, setEditingStopId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    setOffset(0);
  }, []);

  const panelOpen = isCreating || !!editingStopId;

  const { data, isLoading, isError, refetch } = useGetStops({
    search: search || undefined,
    limit: PAGE_SIZE,
    offset,
    sort_order: sortOrder,
  });

  const { createStop, updateStop, deleteStop, isMutating } = useStopsApi();

  // Fetch cities for name lookup in table
  const { data: cityData } = useGetSearchCities({ limit: 100 });
  const cityNameMap = useMemo(() => {
    const map: Record<string, string> = {};
    for (const city of cityData?.items ?? []) {
      map[city.id] = city.name;
    }
    return map;
  }, [cityData?.items]);

  const stops = useMemo(() => data?.items ?? [], [data?.items]);
  const total = data?.total ?? 0;

  const handleSortToggle = () => {
    setSortOrder((prev) =>
      prev === SortOrder.asc ? SortOrder.desc : SortOrder.asc,
    );
    setOffset(0);
  };

  const handleOffsetChange = (newOffset: number) => {
    setOffset(newOffset);
  };

  const editingStop = useMemo(
    () => stops.find((s) => s.id === editingStopId) ?? null,
    [stops, editingStopId],
  );

  const openCreatePanel = () => {
    setEditingStopId(null);
    setIsCreating(true);
  };

  const openEditPanel = (stop: StopRead) => {
    setIsCreating(false);
    setEditingStopId(stop.id);
  };

  const closePanel = () => {
    setEditingStopId(null);
    setIsCreating(false);
  };

  const handleFormSubmit = (payload: {
    city_id: string;
    name: string;
    latitude: number;
    longitude: number;
  }) => {
    if (editingStop) {
      updateStop(editingStop.id, payload);
    } else {
      createStop(payload, closePanel);
    }
  };

  const handleDelete = () => {
    if (!deleteTarget) return;
    deleteStop(deleteTarget.id, () => {
      if (editingStopId === deleteTarget.id) closePanel();
      setDeleteTarget(null);
    });
  };

  return (
    <AdminPageLayout
      panel={
        panelOpen && (
          <StopFormPanel
            key={editingStopId ?? "new"}
            editingStop={editingStop}
            onClose={closePanel}
            onSubmit={handleFormSubmit}
            isMutating={isMutating}
            initialCityLabel={
              editingStop ? (cityNameMap[editingStop.city_id] ?? "") : ""
            }
          />
        )
      }
    >
      <StopsHeader onAddStop={openCreatePanel} />
      <StopSearchInput value={search} onChange={handleSearchChange} />
      <StopsTable
        stops={stops}
        isLoading={isLoading}
        isError={isError}
        onRetry={refetch}
        search={search}
        editingStopId={editingStopId ?? undefined}
        onEdit={openEditPanel}
        onDelete={setDeleteTarget}
        sortOrder={sortOrder}
        onSortToggle={handleSortToggle}
        offset={offset}
        limit={PAGE_SIZE}
        total={total}
        onOffsetChange={handleOffsetChange}
        cityNameMap={cityNameMap}
      />

      <DeleteStopDialog
        stop={deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        disabled={isMutating}
      />
    </AdminPageLayout>
  );
}
