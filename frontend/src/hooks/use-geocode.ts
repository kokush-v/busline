import { useEffect, useRef } from "react";
import type { UseFormSetValue } from "react-hook-form";

type UseGeocodeParams = {
  name: string;
  latitude: number | undefined;
  longitude: number | undefined;
  setValue: UseFormSetValue<{
    latitude: number;
    longitude: number;
    name: string;
  }>;
};

const DEFAULT_CENTER: [number, number] = [48.38, 31.17];

export function useGeocode({
  name,
  latitude,
  longitude,
  setValue,
}: UseGeocodeParams) {
  const prevName = useRef(name);

  useEffect(() => {
    if (prevName.current === name) return;
    prevName.current = name;

    if (!name || name.trim().length < 2) return;

    const timer = setTimeout(async () => {
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
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [name, setValue]);

  const hasCoords =
    latitude != null &&
    longitude != null &&
    !isNaN(latitude) &&
    !isNaN(longitude);

  const mapCenter: [number, number] = hasCoords
    ? [latitude, longitude]
    : DEFAULT_CENTER;

  return { hasCoords, mapCenter };
}
