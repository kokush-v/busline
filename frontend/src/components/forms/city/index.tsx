"use client";

import { useCallback } from "react";
import { useForm, useWatch } from "react-hook-form";
import { standardSchemaResolver } from "@hookform/resolvers/standard-schema";
import { XIcon } from "lucide-react";
import dynamic from "next/dynamic";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { useGeocode } from "@/hooks/use-geocode";
import { cityFormSchema, type CityFormValues } from "./schema";
import type { CityFormPanelProps } from "./types";

const CityMap = dynamic(() => import("@/components/cities/city-map"), {
  ssr: false,
});

export function CityFormPanel({
  editingCity,
  onClose,
  onSubmit,
  isMutating,
}: CityFormPanelProps) {
  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<CityFormValues>({
    resolver: standardSchemaResolver(cityFormSchema),
    defaultValues: editingCity
      ? {
          name: editingCity.name,
          latitude: editingCity.latitude,
          longitude: editingCity.longitude,
        }
      : { name: "", latitude: undefined, longitude: undefined },
  });

  const name = useWatch({ control, name: "name" });
  const latitude = useWatch({ control, name: "latitude" });
  const longitude = useWatch({ control, name: "longitude" });

  const handleMapClick = useCallback(
    (lat: number, lng: number) => {
      setValue("latitude", Number(lat.toFixed(6)));
      setValue("longitude", Number(lng.toFixed(6)));
    },
    [setValue],
  );

  const { hasCoords, mapCenter } = useGeocode({
    name,
    latitude,
    longitude,
    setValue,
  });

  return (
    <div className="-my-8 -mr-3 flex w-96 shrink-0 flex-col border-l px-6 py-6 sm:-mr-4">
      <div className="mb-4 flex items-center justify-between">
        <Text role="h4">{editingCity ? "Edit City" : "Add City"}</Text>
        <Button variant="ghost" size="icon-sm" onClick={onClose}>
          <XIcon className="size-4" />
        </Button>
      </div>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="flex flex-1 flex-col gap-4"
      >
        <FormField id="city-name" label="Name" error={errors.name?.message}>
          <Input id="city-name" placeholder="Kyiv" {...register("name")} />
        </FormField>

        <div className="grid grid-cols-2 gap-3">
          <FormField
            id="city-lat"
            label="Latitude"
            error={errors.latitude?.message}
          >
            <Input
              id="city-lat"
              type="number"
              step="any"
              placeholder="50.4501"
              {...register("latitude")}
            />
          </FormField>
          <FormField
            id="city-lng"
            label="Longitude"
            error={errors.longitude?.message}
          >
            <Input
              id="city-lng"
              type="number"
              step="any"
              placeholder="30.5234"
              {...register("longitude")}
            />
          </FormField>
        </div>

        <FormField id="city-map" label="Pick on map">
          <div className="h-52 overflow-hidden rounded-md border">
            <CityMap
              center={mapCenter}
              markerPosition={hasCoords ? [latitude, longitude] : null}
              onClick={handleMapClick}
            />
          </div>
        </FormField>

        <div className="mt-auto flex gap-2 pt-4">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button type="submit" className="flex-1" disabled={isMutating}>
            {editingCity ? "Save" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
