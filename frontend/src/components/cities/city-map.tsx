"use client";

import { useEffect, useRef } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  useMap,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)
  ._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

type CityMapProps = {
  center: [number, number];
  markerPosition: [number, number] | null;
  onClick: (lat: number, lng: number) => void;
};

function ClickHandler({
  onClick,
}: {
  onClick: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click(e) {
      onClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function RecenterMap({ center }: { center: [number, number] }) {
  const map = useMap();
  const prevCenter = useRef(center);

  useEffect(() => {
    const [prevLat, prevLng] = prevCenter.current;
    const [lat, lng] = center;
    if (prevLat !== lat || prevLng !== lng) {
      map.setView(center, map.getZoom());
      prevCenter.current = center;
    }
  }, [center, map]);

  return null;
}

export default function CityMap({
  center,
  markerPosition,
  onClick,
}: CityMapProps) {
  return (
    <MapContainer
      center={center}
      zoom={6}
      className="h-full w-full"
      style={{ minHeight: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickHandler onClick={onClick} />
      <RecenterMap center={center} />
      {markerPosition && <Marker position={markerPosition} />}
    </MapContainer>
  );
}
