"use client";

import { useState, useCallback, useRef } from "react";
import { useForm, useWatch } from "react-hook-form";
import { standardSchemaResolver } from "@hookform/resolvers/standard-schema";
import { useQueryClient } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import * as PopoverPrimitive from "@radix-ui/react-popover";
import {
  CheckIcon,
  ChevronsUpDownIcon,
  Loader2Icon,
  SearchIcon,
} from "lucide-react";
import { toast } from "sonner";
import {
  usePostStop,
  getGetSearchStopsQueryKey,
} from "@/generated/api/endpoints/stops/stops";
import { useGetSearchCities } from "@/generated/api/endpoints/cities/cities";
import { getErrorMessage } from "@/lib/api/error-handler";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { cn } from "@/lib/utils";
import { stopFormSchema, type StopFormValues } from "./schema";
import type { StopRead } from "@/generated/api/model";

const CityMap = dynamic(() => import("@/components/cities/city-map"), {
  ssr: false,
});

type CreateStopDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: (stop: StopRead) => void;
};

export function CreateStopDialog({
  open,
  onOpenChange,
  onCreated,
}: CreateStopDialogProps) {
  const queryClient = useQueryClient();
  const postStopMutation = usePostStop();
  const inputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    setValue,
    control,
    reset,
    formState: { errors },
  } = useForm<StopFormValues>({
    resolver: standardSchemaResolver(stopFormSchema),
    defaultValues: {
      city_id: "",
      name: "",
      latitude: undefined as unknown as number,
      longitude: undefined as unknown as number,
    },
  });

  const cityId = useWatch({ control, name: "city_id" });
  const name = useWatch({ control, name: "name" });
  const latitude = useWatch({ control, name: "latitude" });
  const longitude = useWatch({ control, name: "longitude" });

  // City search
  const [citySearch, setCitySearch] = useState("");
  const [cityPopoverOpen, setCityPopoverOpen] = useState(false);
  const [cityLabel, setCityLabel] = useState("");
  const debouncedCitySearch = useDebouncedValue(citySearch, 300);

  const { data: cityData, isLoading: citiesLoading } = useGetSearchCities(
    { search: debouncedCitySearch || undefined, limit: 20 },
    { query: { enabled: open && cityPopoverOpen } },
  );

  const [isGeocoding, setIsGeocoding] = useState(false);

  const handleMapClick = useCallback(
    (lat: number, lng: number) => {
      setValue("latitude", Number(lat.toFixed(6)));
      setValue("longitude", Number(lng.toFixed(6)));
    },
    [setValue],
  );

  const handleGeocode = useCallback(async () => {
    if (!name || name.trim().length < 2) return;
    setIsGeocoding(true);
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(name.trim())}&format=json&limit=1`,
      );
      const data = await res.json();
      if (data.length > 0) {
        setValue("latitude", Number(Number(data[0].lat).toFixed(6)));
        setValue("longitude", Number(Number(data[0].lon).toFixed(6)));
      }
    } catch {
      // ignore geocoding errors
    } finally {
      setIsGeocoding(false);
    }
  }, [name, setValue]);

  const DEFAULT_CENTER: [number, number] = [48.38, 31.17];
  const hasCoords =
    latitude != null &&
    longitude != null &&
    !isNaN(latitude) &&
    !isNaN(longitude);
  const mapCenter: [number, number] = hasCoords
    ? [latitude, longitude]
    : DEFAULT_CENTER;

  const onSubmit = (data: StopFormValues) => {
    postStopMutation.mutate(
      { data },
      {
        onSuccess: (newStop) => {
          toast.success("Stop created successfully.");
          queryClient.invalidateQueries({
            queryKey: getGetSearchStopsQueryKey(),
          });
          reset();
          setCitySearch("");
          setCityLabel("");
          onCreated(newStop);
          onOpenChange(false);
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Create New Stop</DialogTitle>
          <DialogDescription>
            Add a new bus stop to the system.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <FormField
            id="stop-city"
            label="City"
            error={errors.city_id?.message}
          >
            <PopoverPrimitive.Root
              open={cityPopoverOpen}
              onOpenChange={setCityPopoverOpen}
            >
              <PopoverPrimitive.Trigger asChild>
                <button
                  type="button"
                  className={cn(
                    "border-input bg-background ring-offset-background flex h-9 w-full items-center justify-between rounded-md border px-3 py-2 text-sm",
                    "focus:ring-ring focus:ring-2 focus:ring-offset-2 focus:outline-none",
                    !cityId && "text-muted-foreground",
                  )}
                >
                  <span className="truncate">
                    {cityLabel || "Select a city..."}
                  </span>
                  {citiesLoading ? (
                    <Loader2Icon className="size-4 shrink-0 animate-spin opacity-50" />
                  ) : (
                    <ChevronsUpDownIcon className="size-4 shrink-0 opacity-50" />
                  )}
                </button>
              </PopoverPrimitive.Trigger>
              <PopoverPrimitive.Portal>
                <PopoverPrimitive.Content
                  className="bg-popover text-popover-foreground z-[100] w-[var(--radix-popover-trigger-width)] rounded-md border shadow-md"
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
                      placeholder="Search cities..."
                      value={citySearch}
                      onChange={(e) => setCitySearch(e.target.value)}
                    />
                  </div>
                  <div className="max-h-48 overflow-y-auto p-1">
                    {citiesLoading ? (
                      <div className="flex items-center justify-center py-4">
                        <Loader2Icon className="size-4 animate-spin" />
                      </div>
                    ) : !cityData?.items.length ? (
                      <div className="text-muted-foreground py-4 text-center text-sm">
                        No cities found.
                      </div>
                    ) : (
                      cityData.items.map((city) => (
                        <button
                          key={city.id}
                          type="button"
                          className={cn(
                            "hover:bg-accent hover:text-accent-foreground relative flex w-full cursor-pointer items-center rounded-sm py-1.5 pr-2 pl-8 text-sm outline-none select-none",
                            cityId === city.id && "bg-accent",
                          )}
                          onClick={() => {
                            setValue("city_id", city.id, {
                              shouldValidate: true,
                            });
                            setCityLabel(city.name);
                            setCityPopoverOpen(false);
                          }}
                        >
                          {cityId === city.id && (
                            <CheckIcon className="absolute left-2 size-4" />
                          )}
                          {city.name}
                        </button>
                      ))
                    )}
                  </div>
                </PopoverPrimitive.Content>
              </PopoverPrimitive.Portal>
            </PopoverPrimitive.Root>
          </FormField>

          <FormField id="stop-name" label="Name" error={errors.name?.message}>
            <div className="flex gap-2">
              <Input
                id="stop-name"
                placeholder="Central Station"
                {...register("name")}
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleGeocode}
                disabled={isGeocoding || !name || name.trim().length < 2}
                title="Find on map"
              >
                {isGeocoding ? (
                  <Loader2Icon className="size-4 animate-spin" />
                ) : (
                  <SearchIcon className="size-4" />
                )}
              </Button>
            </div>
          </FormField>

          <div className="grid grid-cols-2 gap-3">
            <FormField
              id="stop-lat"
              label="Latitude"
              error={errors.latitude?.message}
            >
              <Input
                id="stop-lat"
                type="number"
                step="any"
                placeholder="50.4501"
                {...register("latitude")}
              />
            </FormField>
            <FormField
              id="stop-lng"
              label="Longitude"
              error={errors.longitude?.message}
            >
              <Input
                id="stop-lng"
                type="number"
                step="any"
                placeholder="30.5234"
                {...register("longitude")}
              />
            </FormField>
          </div>

          <FormField id="stop-map" label="Pick on map">
            <div className="relative h-52 overflow-hidden rounded-md border">
              <CityMap
                center={mapCenter}
                markerPosition={hasCoords ? [latitude, longitude] : null}
                onClick={handleMapClick}
              />
              {/* Center pin overlay */}
              {!hasCoords && (
                <div className="pointer-events-none absolute inset-0 z-[1000] flex items-center justify-center">
                  <div className="flex flex-col items-center">
                    <svg
                      width="25"
                      height="41"
                      viewBox="0 0 25 41"
                      className="drop-shadow-md"
                    >
                      <path
                        d="M12.5 0C5.6 0 0 5.6 0 12.5 0 21.9 12.5 41 12.5 41S25 21.9 25 12.5C25 5.6 19.4 0 12.5 0z"
                        fill="#ef4444"
                        opacity="0.5"
                      />
                      <circle
                        cx="12.5"
                        cy="12.5"
                        r="5"
                        fill="white"
                        opacity="0.8"
                      />
                    </svg>
                  </div>
                </div>
              )}
            </div>
          </FormField>

          <div className="flex gap-2 pt-2">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={postStopMutation.isPending}
            >
              Create
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
