"use client";

import { useState, useMemo, useCallback } from "react";
import { toast } from "sonner";
import { useGetCities } from "@/generated/api/endpoints/cities/cities";
import type { CityRead } from "@/generated/api/model";
import { CitySortBy } from "@/generated/api/model/citySortBy";
import { SortOrder } from "@/generated/api/model/sortOrder";
import { useCitiesApi } from "@/hooks/use-cities-api";
import {
  CitiesHeader,
  CitySearchInput,
  CitiesTable,
  CityFormPanel,
  DeleteCityDialog,
} from "@/components/cities";

const PAGE_SIZE = 20;

export default function CitiesPage() {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const [sortBy, setSortBy] = useState<CitySortBy>(CitySortBy.name);
  const [sortOrder, setSortOrder] = useState<SortOrder>(SortOrder.asc);
  const [deleteTarget, setDeleteTarget] = useState<CityRead | null>(null);
  const [editingCityId, setEditingCityId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const handleSearchChange = useCallback((value: string) => {
    setSearch(value);
    setOffset(0);
  }, []);

  const panelOpen = isCreating || !!editingCityId;

  const { data, isLoading } = useGetCities({
    search: search || undefined,
    limit: PAGE_SIZE,
    offset,
    sort_by: sortBy,
    sort_order: sortOrder,
  });

  const { createCity, updateCity, deleteCity, isMutating } = useCitiesApi();

  const cities = useMemo(() => data?.items ?? [], [data?.items]);
  const total = data?.total ?? 0;

  const handleSortChange = (field: CitySortBy) => {
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

  const editingCity = useMemo(
    () => cities.find((c) => c.id === editingCityId) ?? null,
    [cities, editingCityId],
  );

  const openCreatePanel = () => {
    setEditingCityId(null);
    setIsCreating(true);
  };

  const openEditPanel = (city: CityRead) => {
    setIsCreating(false);
    setEditingCityId(city.id);
  };

  const closePanel = () => {
    setEditingCityId(null);
    setIsCreating(false);
  };

  const handleFormSubmit = (payload: {
    name: string;
    longitude: number;
    latitude: number;
  }) => {
    if (!payload.name) {
      toast.error("City name is required.");
      return;
    }

    if (editingCity) {
      updateCity(editingCity.id, payload);
    } else {
      createCity(payload, closePanel);
    }
  };

  const handleDelete = () => {
    if (!deleteTarget) return;
    deleteCity(deleteTarget.id, () => {
      if (editingCityId === deleteTarget.id) closePanel();
      setDeleteTarget(null);
    });
  };

  return (
    <div className="flex flex-1 gap-6">
      <div className="flex min-w-0 flex-1 flex-col gap-6">
        <CitiesHeader onAddCity={openCreatePanel} />
        <CitySearchInput value={search} onChange={handleSearchChange} />
        <CitiesTable
          cities={cities}
          isLoading={isLoading}
          search={search}
          editingCityId={editingCityId ?? undefined}
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
      </div>

      {panelOpen && (
        <CityFormPanel
          key={editingCityId ?? "new"}
          editingCity={editingCity}
          onClose={closePanel}
          onSubmit={handleFormSubmit}
          isMutating={isMutating}
        />
      )}

      <DeleteCityDialog
        city={deleteTarget}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
        disabled={isMutating}
      />
    </div>
  );
}
