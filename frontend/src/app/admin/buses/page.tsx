"use client";

import { useState, useMemo, useCallback } from "react";
import { useGetBuses } from "@/generated/api/endpoints/buses/buses";
import type { BusRead } from "@/generated/api/model";
import { BusSortBy } from "@/generated/api/model/busSortBy";
import { SortOrder } from "@/generated/api/model/sortOrder";
import { useBusesApi } from "@/hooks/use-buses-api";
import { useBusImageUpload } from "@/hooks/use-bus-image-upload";
import {
  BusesHeader,
  BusSearchInput,
  BusesTable,
  BusFormPanel,
  DeleteBusDialog,
} from "@/components/buses";
import { AdminPageLayout } from "@/components/admin/admin-page-layout";

const PAGE_SIZE = 20;

export default function BusesPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [sortBy, setSortBy] = useState<BusSortBy>(BusSortBy.number_plate);
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.asc);
  const [deleteTarget, setDeleteTarget] = useState<BusRead | null>(null);
  const [editingBusId, setEditingBusId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    setOffset(0);
  }, []);

  const panelOpen = isCreating || !!editingBusId;

  const { data, isLoading, isError, refetch } = useGetBuses({
    search: search || undefined,
    limit: PAGE_SIZE,
    offset,
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  const { createBus, updateBus, deleteBus, isMutating } = useBusesApi();
  const { uploadToS3, saveImage, removeImage, isUploading, isDeleting } =
    useBusImageUpload();

  const buses = useMemo(() => data?.items ?? [], [data?.items]);
  const total = data?.total ?? 0;

  const handleSortChange = (field: BusSortBy) => {
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

  const editingBus = useMemo(
    () => buses.find((b) => b.id === editingBusId) ?? null,
    [buses, editingBusId],
  );

  const openCreatePanel = () => {
    setEditingBusId(null);
    setIsCreating(true);
  };

  const openEditPanel = (bus: BusRead) => {
    setIsCreating(false);
    setEditingBusId(bus.id);
  };

  const closePanel = () => {
    setEditingBusId(null);
    setIsCreating(false);
  };

  const handleFormSubmit = async (payload: {
    number_plate: string;
    color: string;
    seats_quantity: number;
    photoKey: string | null;
  }) => {
    const { photoKey, ...busPayload } = payload;

    if (editingBus) {
      updateBus(editingBus.id, busPayload, async () => {
        if (photoKey) {
          await saveImage(editingBus.id, photoKey);
        }
      });
    } else {
      createBus(busPayload, async (bus) => {
        setIsCreating(false);
        setEditingBusId(bus.id);
        if (photoKey) {
          await saveImage(bus.id, photoKey);
        }
      });
    }
  };

  const handleDeleteImage = async (busId: string) => {
    await removeImage(busId);
  };

  const handleDelete = () => {
    if (!deleteTarget) return;
    deleteBus(deleteTarget.id, () => {
      if (editingBusId === deleteTarget.id) closePanel();
      setDeleteTarget(null);
    });
  };

  return (
    <AdminPageLayout
      panel={
        panelOpen && (
          <BusFormPanel
            key={editingBusId ?? "new"}
            editingBus={editingBus}
            onClose={closePanel}
            onSubmit={handleFormSubmit}
            onUpload={uploadToS3}
            onDeleteImage={handleDeleteImage}
            isMutating={isMutating}
            isUploading={isUploading}
            isDeleting={isDeleting}
          />
        )
      }
    >
      <BusesHeader onAddBus={openCreatePanel} />
      <BusSearchInput value={search} onChange={handleSearchChange} />
      <BusesTable
        buses={buses}
        isLoading={isLoading}
        isError={isError}
        onRetry={refetch}
        search={search}
        editingBusId={editingBusId ?? undefined}
        onEdit={openEditPanel}
        onDelete={setDeleteTarget}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSortChange}
        offset={offset}
        limit={PAGE_SIZE}
        total={total}
        onOffsetChange={handleOffsetChange}
      />

      <DeleteBusDialog
        bus={deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        disabled={isMutating}
      />
    </AdminPageLayout>
  );
}
