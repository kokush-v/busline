import { useState, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { getErrorMessage } from "@/lib/api/error-handler";
import {
  postImageUploadUrl,
  usePostImageSave,
  useDeleteImage,
  getGetBusesQueryKey,
} from "@/generated/api/endpoints/buses/buses";

export function useBusImageUpload() {
  const queryClient = useQueryClient();
  const saveMutation = usePostImageSave();
  const deleteMutation = useDeleteImage();
  const [isUploading, setIsUploading] = useState(false);

  const invalidate = useCallback(
    () => queryClient.invalidateQueries({ queryKey: getGetBusesQueryKey() }),
    [queryClient],
  );

  const uploadToS3 = useCallback(async (file: File): Promise<string> => {
    setIsUploading(true);
    try {
      const { upload_url, photo_key, fields } = await postImageUploadUrl({
        content_type: file.type,
      });

      const formData = new FormData();
      if (fields) {
        Object.entries(fields).forEach(([key, value]) => {
          formData.append(key, value);
        });
      }
      formData.append("file", file);

      const response = await fetch(upload_url, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload image to storage");
      }

      return photo_key;
    } finally {
      setIsUploading(false);
    }
  }, []);

  const saveImage = useCallback(
    (busId: string, photoKey: string): Promise<void> => {
      return new Promise((resolve, reject) => {
        saveMutation.mutate(
          { busId, data: { photo_key: photoKey } },
          {
            onSuccess: () => {
              toast.success("Photo saved successfully.");
              invalidate();
              resolve();
            },
            onError: (error) => {
              toast.error(getErrorMessage(error));
              reject(error);
            },
          },
        );
      });
    },
    [saveMutation, invalidate],
  );

  const removeImage = useCallback(
    (busId: string): Promise<void> => {
      return new Promise((resolve, reject) => {
        deleteMutation.mutate(
          { busId },
          {
            onSuccess: () => {
              toast.success("Photo deleted.");
              invalidate();
              resolve();
            },
            onError: (error) => {
              toast.error(getErrorMessage(error));
              reject(error);
            },
          },
        );
      });
    },
    [deleteMutation, invalidate],
  );

  const isSaving = saveMutation.isPending || deleteMutation.isPending;
  const isDeleting = deleteMutation.isPending;

  return {
    uploadToS3,
    saveImage,
    removeImage,
    isUploading,
    isSaving,
    isDeleting,
  };
}
