import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getErrorMessage } from "@/lib/api/error-handler";
import {
  usePostCity,
  usePutCity,
  useDeleteCity,
  getGetCitiesQueryKey,
} from "@/generated/api/endpoints/cities/cities";

interface CityPayload {
  name: string;
  longitude: number;
  latitude: number;
}

export function useCitiesApi() {
  const queryClient = useQueryClient();
  const createMutation = usePostCity();
  const updateMutation = usePutCity();
  const deleteMutation = useDeleteCity();

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: getGetCitiesQueryKey() });

  const createCity = (payload: CityPayload, onSuccess?: () => void) => {
    createMutation.mutate(
      { data: payload },
      {
        onSuccess: () => {
          toast.success("City created successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const updateCity = (
    cityId: string,
    payload: CityPayload,
    onSuccess?: () => void,
  ) => {
    updateMutation.mutate(
      { cityId, data: payload },
      {
        onSuccess: () => {
          toast.success("City updated successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const deleteCity = (cityId: string, onSuccess?: () => void) => {
    deleteMutation.mutate(
      { cityId },
      {
        onSuccess: () => {
          toast.success("City deleted successfully.");
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

  return { createCity, updateCity, deleteCity, isMutating };
}
