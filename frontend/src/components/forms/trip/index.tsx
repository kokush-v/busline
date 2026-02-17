"use client";

import { useEffect } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { ImageIcon } from "lucide-react";
import { useGetBuses } from "@/generated/api/endpoints/buses/buses";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { Combobox } from "@/components/ui/combobox";
import { LoadingImage } from "@/components/ui/loading-image";
import { SortableStopItem } from "./sortable-stop-item";
import { AddStopSection } from "./add-stop-section";
import { tripFormSchema, type TripFormValues } from "./schema";
import type { TripFormProps } from "./types";

export function TripForm({
  defaultValues,
  selectedStops,
  onStopAdd,
  onStopRemove,
  onStopReorder,
  onSubmit,
  onCancel,
  isMutating,
  isEdit,
}: TripFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    control,
    formState: { errors },
  } = useForm<TripFormValues>({
    resolver: zodResolver(tripFormSchema),
    defaultValues: defaultValues ?? {
      bus_id: "",
      price_per_seat: 0,
      stops: [],
    },
  });

  const { fields, replace } = useFieldArray({
    control,
    name: "stops",
  });

  const busId = watch("bus_id");

  const { data: busData, isLoading: busesLoading } = useGetBuses({
    limit: 100,
  });

  const busOptions = (busData?.items ?? []).map((b) => ({
    value: b.id,
    label: `${b.number_plate} (${b.seats_quantity} seats)`,
  }));

  // Sync selectedStops with form fields
  const selectedStopIds = selectedStops.map((s) => s.id);

  useEffect(() => {
    const currentStops = fields.map((f) => f.stop_id);
    const isSame =
      currentStops.length === selectedStopIds.length &&
      currentStops.every((id, i) => id === selectedStopIds[i]);

    if (!isSame) {
      const newStops = selectedStopIds.map((stopId) => {
        const existing = fields.find((f) => f.stop_id === stopId);
        return {
          stop_id: stopId,
          arrival_time: existing?.arrival_time ?? "",
          departure_time: existing?.departure_time ?? "",
        };
      });
      replace(newStops);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStopIds.join(",")]);

  const getStopName = (stopId: string) =>
    selectedStops.find((s) => s.id === stopId)?.name ?? "Unknown stop";

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = fields.findIndex((f) => f.id === active.id);
    const newIndex = fields.findIndex((f) => f.id === over.id);
    if (oldIndex !== -1 && newIndex !== -1) {
      onStopReorder(oldIndex, newIndex);
    }
  };

  return (
    <div className="flex h-full flex-col overflow-y-auto border-l bg-white dark:bg-transparent">
      <div className="border-b px-6 py-4">
        <Text role="h4">{isEdit ? "Edit Trip" : "New Trip"}</Text>
      </div>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex flex-1 flex-col gap-4 overflow-y-auto px-6 py-4"
      >
        {isEdit ? (
          (() => {
            const bus = (busData?.items ?? []).find((b) => b.id === busId);
            if (!bus) return null;
            return (
              <div className="space-y-1.5">
                <Text role="label" className="text-sm font-medium">
                  Bus
                </Text>
                <div className="bg-muted/40 flex items-center gap-3 rounded-md border p-3">
                  <LoadingImage
                    src={bus.thumbnail_url ?? undefined}
                    alt={bus.number_plate}
                    className="size-12 shrink-0 rounded object-cover"
                    fallback={
                      <div className="bg-muted flex size-12 shrink-0 items-center justify-center rounded">
                        <ImageIcon className="text-muted-foreground size-4" />
                      </div>
                    }
                  />
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">
                      {bus.number_plate}
                    </p>
                    <p className="text-muted-foreground text-xs">
                      {bus.color} &middot; {bus.seats_quantity} seats
                    </p>
                  </div>
                </div>
              </div>
            );
          })()
        ) : (
          <FormField id="trip-bus" label="Bus" error={errors.bus_id?.message}>
            <Combobox
              options={busOptions}
              value={busId}
              onChange={(val) =>
                setValue("bus_id", val, { shouldValidate: true })
              }
              placeholder="Select a bus..."
              isLoading={busesLoading}
            />
          </FormField>
        )}

        <FormField
          id="trip-price"
          label="Price per seat"
          error={errors.price_per_seat?.message}
        >
          <Input
            id="trip-price"
            type="number"
            min={0}
            step="0.01"
            placeholder="0.00"
            {...register("price_per_seat")}
          />
        </FormField>

        <div className="space-y-2">
          <Text role="label" className="text-sm font-medium">
            Route stops ({fields.length})
          </Text>
          {errors.stops?.root?.message && (
            <p className="text-destructive text-sm">
              {errors.stops.root.message}
            </p>
          )}
          {errors.stops?.message && (
            <p className="text-destructive text-sm">{errors.stops.message}</p>
          )}

          {fields.length === 0 ? (
            <p className="text-muted-foreground py-4 text-center text-sm">
              Use the button below to add stops to the route.
            </p>
          ) : (
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={fields.map((f) => f.id)}
                strategy={verticalListSortingStrategy}
              >
                <div className="space-y-3">
                  {fields.map((field, index) => (
                    <SortableStopItem
                      key={field.id}
                      field={field}
                      index={index}
                      stopName={getStopName(field.stop_id)}
                      onRemove={() => onStopRemove(field.stop_id)}
                      register={register}
                      errors={errors}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext>
          )}

          <div className="pt-2">
            <AddStopSection
              selectedStops={selectedStops}
              onStopAdd={onStopAdd}
            />
          </div>
        </div>

        <div className="mt-auto flex gap-2 border-t pt-4">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={onCancel}
          >
            Cancel
          </Button>
          <Button type="submit" className="flex-1" disabled={isMutating}>
            {isEdit ? "Save" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
