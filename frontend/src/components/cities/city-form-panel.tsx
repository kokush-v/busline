"use client";

import { useState, useCallback, useRef } from "react";
import { XIcon } from "lucide-react";
import dynamic from "next/dynamic";
import type { CityRead } from "@/generated/api/model";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const CityMap = dynamic(() => import("./city-map"), { ssr: false });

type CityFormData = {
  name: string;
  longitude: string;
  latitude: string;
};

const emptyCityForm: CityFormData = { name: "", longitude: "", latitude: "" };

type CityFormPanelProps = {
  editingCity: CityRead | null;
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    longitude: number;
    latitude: number;
  }) => void;
  isMutating: boolean;
};

export function CityFormPanel({
  editingCity,
  onClose,
  onSubmit,
  isMutating,
}: CityFormPanelProps) {
  const [form, setForm] = useState<CityFormData>(() =>
    editingCity
      ? {
          name: editingCity.name,
          longitude: String(editingCity.longitude),
          latitude: String(editingCity.latitude),
        }
      : emptyCityForm,
  );
  const geocodeTimer = useRef<ReturnType<typeof setTimeout>>(null);

  const geocodeName = useCallback((name: string) => {
    if (geocodeTimer.current) clearTimeout(geocodeTimer.current);
    if (name.trim().length < 2) return;

    geocodeTimer.current = setTimeout(async () => {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(name.trim())}&format=json&limit=1`,
        );
        const data = await res.json();
        if (data.length > 0) {
          setForm((prev) => ({
            ...prev,
            latitude: Number(data[0].lat).toFixed(6),
            longitude: Number(data[0].lon).toFixed(6),
          }));
        }
      } catch {}
    }, 500);
  }, []);

  const handleMapClick = useCallback((lat: number, lng: number) => {
    setForm((prev) => ({
      ...prev,
      latitude: lat.toFixed(6),
      longitude: lng.toFixed(6),
    }));
  }, []);

  const handleSubmit = () => {
    onSubmit({
      name: form.name.trim(),
      longitude: Number(form.longitude),
      latitude: Number(form.latitude),
    });
  };

  const mapCenter: [number, number] =
    form.latitude && form.longitude
      ? [Number(form.latitude), Number(form.longitude)]
      : [48.38, 31.17];

  return (
    <div className="-my-8 -mr-3 flex w-96 shrink-0 flex-col border-l px-6 py-6 sm:-mr-4">
      <div className="mb-4 flex items-center justify-between">
        <Text role="h4">{editingCity ? "Edit City" : "Add City"}</Text>
        <Button variant="ghost" size="icon-sm" onClick={onClose}>
          <XIcon className="size-4" />
        </Button>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        className="flex flex-1 flex-col gap-4"
      >
        <div className="flex flex-col gap-2">
          <Label htmlFor="city-name">Name</Label>
          <Input
            id="city-name"
            value={form.name}
            onChange={(e) => {
              const val = e.target.value;
              setForm((prev) => ({ ...prev, name: val }));
              geocodeName(val);
            }}
            placeholder="Kyiv"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex flex-col gap-2">
            <Label htmlFor="city-lat">Latitude</Label>
            <Input
              id="city-lat"
              type="number"
              step="any"
              value={form.latitude}
              onChange={(e) =>
                setForm((prev) => ({
                  ...prev,
                  latitude: e.target.value,
                }))
              }
              placeholder="50.4501"
              required
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="city-lng">Longitude</Label>
            <Input
              id="city-lng"
              type="number"
              step="any"
              value={form.longitude}
              onChange={(e) =>
                setForm((prev) => ({
                  ...prev,
                  longitude: e.target.value,
                }))
              }
              placeholder="30.5234"
              required
            />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <Label>Pick on map</Label>
          <div className="min-h-50 flex-1 overflow-hidden rounded-md border">
            <CityMap
              center={mapCenter}
              markerPosition={
                form.latitude && form.longitude
                  ? [Number(form.latitude), Number(form.longitude)]
                  : null
              }
              onClick={handleMapClick}
            />
          </div>
        </div>

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
