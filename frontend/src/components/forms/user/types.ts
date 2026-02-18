import type { UserRead } from "@/generated/api/model";
import type { UserCreateFormValues, UserUpdateFormValues } from "./schema";

export type UserFormPanelProps = {
  editingUser: UserRead | null;
  onClose: () => void;
  onSubmit: (data: UserCreateFormValues | UserUpdateFormValues) => void;
  isMutating: boolean;
};
