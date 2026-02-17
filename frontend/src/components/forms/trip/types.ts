import type { useForm } from "react-hook-form";
import type { StopRead } from "@/generated/api/model";
import type { TripFormValues } from "./schema";

export type SelectedStopInfo = {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
};

export type TripFormProps = {
  defaultValues?: TripFormValues;
  selectedStops: SelectedStopInfo[];
  onStopAdd: (stop: StopRead) => void;
  onStopRemove: (stopId: string) => void;
  onStopReorder: (fromIndex: number, toIndex: number) => void;
  onSubmit: (data: TripFormValues) => void;
  onCancel: () => void;
  isMutating: boolean;
  isEdit?: boolean;
};

export type SortableStopItemProps = {
  field: {
    id: string;
    stop_id: string;
    arrival_time: string;
    departure_time: string;
  };
  index: number;
  stopName: string;
  onRemove: () => void;
  register: ReturnType<typeof useForm<TripFormValues>>["register"];
  errors: ReturnType<typeof useForm<TripFormValues>>["formState"]["errors"];
};
