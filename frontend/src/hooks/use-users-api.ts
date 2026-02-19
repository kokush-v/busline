import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getErrorMessage } from "@/lib/api/error-handler";
import {
  usePostUser,
  usePutUser,
  useDeleteUser,
  usePostActivateUser,
  usePostDeactivateUser,
  getGetUsersQueryKey,
} from "@/generated/api/endpoints/users/users";
import type { UserCreate, UserUpdate } from "@/generated/api/model";

export function useUsersApi() {
  const queryClient = useQueryClient();
  const createMutation = usePostUser();
  const updateMutation = usePutUser();
  const deleteMutation = useDeleteUser();
  const activateMutation = usePostActivateUser();
  const deactivateMutation = usePostDeactivateUser();

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: getGetUsersQueryKey() });

  const createUser = (payload: UserCreate, onSuccess?: () => void) => {
    createMutation.mutate(
      { data: payload },
      {
        onSuccess: () => {
          toast.success("User created successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const updateUser = (
    userId: string,
    payload: UserUpdate,
    onSuccess?: () => void,
  ) => {
    updateMutation.mutate(
      { userId, data: payload },
      {
        onSuccess: () => {
          toast.success("User updated successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const deleteUser = (userId: string, onSuccess?: () => void) => {
    deleteMutation.mutate(
      { userId },
      {
        onSuccess: () => {
          toast.success("User deleted successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const activateUser = (userId: string, onSuccess?: () => void) => {
    activateMutation.mutate(
      { userId },
      {
        onSuccess: () => {
          toast.success("User activated successfully.");
          invalidate();
          onSuccess?.();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const deactivateUser = (userId: string, onSuccess?: () => void) => {
    deactivateMutation.mutate(
      { userId },
      {
        onSuccess: () => {
          toast.success("User deactivated successfully.");
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
    deleteMutation.isPending ||
    activateMutation.isPending ||
    deactivateMutation.isPending;

  return {
    createUser,
    updateUser,
    deleteUser,
    activateUser,
    deactivateUser,
    isMutating,
  };
}
