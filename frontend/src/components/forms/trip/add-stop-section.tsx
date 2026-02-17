"use client";

import { useState, useRef } from "react";
import * as PopoverPrimitive from "@radix-ui/react-popover";
import { PlusIcon, Loader2Icon } from "lucide-react";
import {
  useGetSearchStops,
  getStop,
} from "@/generated/api/endpoints/stops/stops";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { Button } from "@/components/ui/button";
import { CreateStopDialog } from "@/components/forms/stop/create-stop-dialog";
import type { StopRead } from "@/generated/api/model";
import type { SelectedStopInfo } from "./types";

type AddStopSectionProps = {
  selectedStops: SelectedStopInfo[];
  onStopAdd: (stop: StopRead) => void;
};

export function AddStopSection({
  selectedStops,
  onStopAdd,
}: AddStopSectionProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [isLoadingStop, setIsLoadingStop] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const debouncedSearch = useDebouncedValue(search, 300);

  const { data: searchData, isLoading: searching } = useGetSearchStops(
    { search: debouncedSearch || undefined, limit: 20 },
    { query: { enabled: open } },
  );

  const selectedIds = new Set(selectedStops.map((s) => s.id));
  const filteredResults = (searchData?.items ?? []).filter(
    (item) => !selectedIds.has(item.id),
  );

  const handleSelectStop = async (stopId: string) => {
    setIsLoadingStop(true);
    try {
      const fullStop = await getStop(stopId);
      onStopAdd(fullStop);
      setOpen(false);
      setSearch("");
    } finally {
      setIsLoadingStop(false);
    }
  };

  const handleCreateNew = () => {
    setOpen(false);
    setSearch("");
    setCreateDialogOpen(true);
  };

  return (
    <>
      <PopoverPrimitive.Root open={open} onOpenChange={setOpen}>
        <PopoverPrimitive.Trigger asChild>
          <Button type="button" variant="outline" size="sm" className="w-full">
            <PlusIcon className="mr-1 size-4" />
            Add stop
          </Button>
        </PopoverPrimitive.Trigger>
        <PopoverPrimitive.Portal>
          <PopoverPrimitive.Content
            className="bg-popover text-popover-foreground z-50 w-[var(--radix-popover-trigger-width)] rounded-md border shadow-md"
            sideOffset={4}
            onOpenAutoFocus={(e) => {
              e.preventDefault();
              inputRef.current?.focus();
            }}
          >
            <div className="p-2">
              <input
                ref={inputRef}
                className="border-input bg-background placeholder:text-muted-foreground w-full rounded-md border px-3 py-1.5 text-sm outline-none"
                placeholder="Search stops..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="max-h-60 overflow-y-auto p-1">
              {/* Create new stop — always first */}
              <button
                type="button"
                className="hover:bg-accent hover:text-accent-foreground flex w-full cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm font-medium outline-none select-none"
                onClick={handleCreateNew}
              >
                <PlusIcon className="size-4" />
                Create new stop
              </button>

              {searching || isLoadingStop ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2Icon className="size-4 animate-spin" />
                </div>
              ) : filteredResults.length === 0 ? (
                <div className="text-muted-foreground py-4 text-center text-sm">
                  No stops found.
                </div>
              ) : (
                filteredResults.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className="hover:bg-accent hover:text-accent-foreground flex w-full cursor-pointer flex-col items-start rounded-sm px-2 py-1.5 text-sm outline-none select-none"
                    onClick={() => handleSelectStop(item.id)}
                  >
                    <span>{item.name}</span>
                    <span className="text-muted-foreground text-xs">
                      {item.city_name}
                    </span>
                  </button>
                ))
              )}
            </div>
          </PopoverPrimitive.Content>
        </PopoverPrimitive.Portal>
      </PopoverPrimitive.Root>

      <CreateStopDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onCreated={onStopAdd}
      />
    </>
  );
}
