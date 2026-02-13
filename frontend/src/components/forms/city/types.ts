import type { CityRead } from "@/generated/api/model";
import type { CityFormValues } from "./schema";

export type CityFormPanelProps = {
  editingCity: CityRead | null;
  onClose: () => void;
  onSubmit: (data: CityFormValues) => void;
  isMutating: boolean;
};
