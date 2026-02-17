"use client";

import { useEffect, useMemo } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Polyline,
  Tooltip,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { SelectedStopInfo } from "@/components/forms/trip/types";

delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)
  ._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const greenIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

function InvalidateSizeOnMount() {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => map.invalidateSize(), 100);
    return () => clearTimeout(timer);
  }, [map]);
  return null;
}

type TripRouteMapProps = {
  stops: SelectedStopInfo[];
};

export default function TripRouteMap({ stops }: TripRouteMapProps) {
  const polylinePositions = useMemo(
    () => stops.map((s) => [s.latitude, s.longitude] as [number, number]),
    [stops],
  );

  const center: [number, number] = useMemo(() => {
    if (stops.length === 0) return [48.5, 31.5]; // Ukraine center
    const avgLat = stops.reduce((sum, s) => sum + s.latitude, 0) / stops.length;
    const avgLng =
      stops.reduce((sum, s) => sum + s.longitude, 0) / stops.length;
    return [avgLat, avgLng];
  }, [stops]);

  return (
    <MapContainer
      center={center}
      zoom={6}
      className="h-full w-full"
      style={{ minHeight: "100%" }}
    >
      <InvalidateSizeOnMount />
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {stops.map((stop, index) => (
        <Marker
          key={stop.id}
          position={[stop.latitude, stop.longitude]}
          icon={greenIcon}
        >
          <Tooltip direction="top" offset={[0, -40]} permanent>
            #{index + 1} {stop.name}
          </Tooltip>
        </Marker>
      ))}

      {polylinePositions.length >= 2 && (
        <Polyline
          positions={polylinePositions}
          pathOptions={{ color: "#22c55e", weight: 3 }}
        />
      )}
    </MapContainer>
  );
}
