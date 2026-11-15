import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getErrorMessage } from "@/lib/api/error-handler";
import {
  usePostStop,
  usePutStop,
  useDeleteStop,
  getGetStopsQueryKey,
} from "@/generated/api/endpoints/stops/stops";

interface StopPayload {
  city_id: string;
  name: string;
  latitude: number;
  longitude: number;
}

interface StopUpdatePayload {
  city_id?: string | null;
  name?: string | null;
  latitude?: number | null;
  longitude?: number | null;
}

export function useStopsApi() {
  const queryClient = useQueryClient();
  const createMutation = usePostStop();
  const updateMutation = usePutStop();
  const deleteMutation = useDeleteStop();

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: getGetStopsQueryKey() });

  const createStop = (payload: StopPayload, onSuccess?: () => void) => {
    createMutation.mutate(
      { data: payload },
      {
        onSuccess: () => {
          toast.success("Stop created successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const updateStop = (
    stopId: string,
    payload: StopUpdatePayload,
    onSuccess?: () => void,
  ) => {
    updateMutation.mutate(
      { stopId, data: payload },
      {
        onSuccess: () => {
          toast.success("Stop updated successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const deleteStop = (stopId: string, onSuccess?: () => void) => {
    deleteMutation.mutate(
      { stopId },
      {
        onSuccess: () => {
          toast.success("Stop deleted successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const isMutating =
    createMutation.isPending ||
    updateMutation.isPending ||
    deleteMutation.isPending;

  return { createStop, updateStop, deleteStop, isMutating };
}
