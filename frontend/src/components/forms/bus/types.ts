import type { BusRead } from "@/generated/api/model";
import type { BusFormValues } from "./schema";

export type BusFormPanelProps = {
  editingBus: BusRead | null;
  onClose: () => void;
  onSubmit: (data: BusFormValues & { photoKey: string | null }) => void;
  onUpload: (file: File) => Promise<string>;
  onDeleteImage?: (busId: string) => Promise<void>;
  isMutating: boolean;
  isUploading: boolean;
  isDeleting?: boolean;
};
