import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getErrorMessage } from "@/lib/api/error-handler";
import {
  usePostTrip,
  usePutTrip,
  useDeleteTrip,
  getGetTripsQueryKey,
} from "@/generated/api/endpoints/trips/trips";
import type { TripCreate, TripUpdate } from "@/generated/api/model";

export function useTripsApi() {
  const queryClient = useQueryClient();
  const createMutation = usePostTrip();
  const updateMutation = usePutTrip();
  const deleteMutation = useDeleteTrip();

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: getGetTripsQueryKey() });

  const createTrip = (payload: TripCreate, onSuccess?: () => void) => {
    createMutation.mutate(
      { data: payload },
      {
        onSuccess: () => {
          toast.success("Trip created successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const updateTrip = (
    tripId: string,
    payload: TripUpdate,
    onSuccess?: () => void,
  ) => {
    updateMutation.mutate(
      { tripId, data: payload },
      {
        onSuccess: () => {
          toast.success("Trip updated successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const deleteTrip = (tripId: string, onSuccess?: () => void) => {
    deleteMutation.mutate(
      { tripId },
      {
        onSuccess: () => {
          toast.success("Trip deleted successfully.");
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

  return { createTrip, updateTrip, deleteTrip, isMutating };
}
