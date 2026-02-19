import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getErrorMessage } from "@/lib/api/error-handler";
import {
  usePostBus,
  usePutBus,
  useDeleteBus,
  getGetBusesQueryKey,
} from "@/generated/api/endpoints/buses/buses";
import type { BusRead } from "@/generated/api/model";

interface BusPayload {
  number_plate: string;
  color: string;
  seats_quantity: number;
}

export function useBusesApi() {
  const queryClient = useQueryClient();
  const createMutation = usePostBus();
  const updateMutation = usePutBus();
  const deleteMutation = useDeleteBus();

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: getGetBusesQueryKey() });

  const createBus = (
    payload: BusPayload,
    onSuccess?: (bus: BusRead) => void,
  ) => {
    createMutation.mutate(
      { data: payload },
      {
        onSuccess: (bus) => {
          toast.success("Bus created successfully.");
          invalidate();
          onSuccess?.(bus);
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const updateBus = (
    busId: string,
    payload: BusPayload,
    onSuccess?: () => void,
  ) => {
    updateMutation.mutate(
      { busId, data: payload },
      {
        onSuccess: () => {
          toast.success("Bus updated successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const deleteBus = (busId: string, onSuccess?: () => void) => {
    deleteMutation.mutate(
      { busId },
      {
        onSuccess: () => {
          toast.success("Bus deleted successfully.");
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

  return { createBus, updateBus, deleteBus, isMutating };
}
