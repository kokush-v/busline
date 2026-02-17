import type { StopRead } from "@/generated/api/model";
import type { StopFormValues } from "./schema";

export type StopFormPanelProps = {
  editingStop: StopRead | null;
  onClose: () => void;
  onSubmit: (data: StopFormValues) => void;
  isMutating: boolean;
  initialCityLabel?: string;
};
