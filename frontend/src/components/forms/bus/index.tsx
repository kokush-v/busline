import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { standardSchemaResolver } from "@hookform/resolvers/standard-schema";
import { XIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import { ColorPicker } from "@/components/ui/color-picker";
import { ImageDropzone } from "@/components/ui/image-dropzone";
import { busFormSchema, type BusFormValues } from "./schema";
import type { BusFormPanelProps } from "./types";

export function BusFormPanel({
  editingBus,
  onClose,
  onSubmit,
  onUpload,
  onDeleteImage,
  isMutating,
  isUploading,
  isDeleting,
}: BusFormPanelProps) {
  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<BusFormValues>({
    resolver: standardSchemaResolver(busFormSchema),
    defaultValues: editingBus
      ? {
          number_plate: editingBus.number_plate,
          color: editingBus.color,
          seats_quantity: editingBus.seats_quantity,
        }
      : { number_plate: "", color: "", seats_quantity: 0 },
  });

  const color = useWatch({ control, name: "color" });

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [photoKey, setPhotoKey] = useState<string | null>(null);

  const handleImageChange = async (file: File | null) => {
    if (!file) {
      setImageFile(null);
      setPhotoKey(null);
      return;
    }

    setImageFile(file);
    try {
      const key = await onUpload(file);
      setPhotoKey(key);
    } catch {
      setImageFile(null);
      setPhotoKey(null);
    }
  };

  const handleDeleteExisting = async () => {
    if (editingBus && onDeleteImage) {
      await onDeleteImage(editingBus.id);
    }
  };

  const onValid = (data: BusFormValues) => {
    onSubmit({ ...data, photoKey });
  };

  const existingImageUrl =
    !imageFile && editingBus ? (editingBus.photo_url ?? null) : null;

  return (
    <div className="-my-8 -mr-3 flex w-96 shrink-0 flex-col border-l px-6 py-6 sm:-mr-4">
      <div className="mb-4 flex items-center justify-between">
        <Text role="h4">{editingBus ? "Edit Bus" : "Add Bus"}</Text>
        <Button variant="ghost" size="icon-sm" onClick={onClose}>
          <XIcon className="size-4" />
        </Button>
      </div>

      <form
        onSubmit={handleSubmit(onValid)}
        className="flex flex-1 flex-col gap-4"
      >
        <FormField id="bus-photo" label="Photo">
          <ImageDropzone
            value={imageFile}
            onChange={handleImageChange}
            existingImageUrl={existingImageUrl}
            onDeleteExisting={handleDeleteExisting}
            isUploading={isUploading}
            isDeleting={isDeleting}
            disabled={isMutating}
          />
        </FormField>

        <FormField
          id="bus-number-plate"
          label="Number Plate"
          error={errors.number_plate?.message}
        >
          <Input
            id="bus-number-plate"
            placeholder="AA1234BB"
            maxLength={20}
            {...register("number_plate")}
          />
        </FormField>

        <FormField id="bus-color" label="Color" error={errors.color?.message}>
          <ColorPicker
            id="bus-color"
            value={color}
            onChange={(val) => setValue("color", val, { shouldValidate: true })}
          />
        </FormField>

        <FormField
          id="bus-seats"
          label="Seats Quantity"
          error={errors.seats_quantity?.message}
        >
          <Input
            id="bus-seats"
            type="number"
            min={0}
            placeholder="50"
            {...register("seats_quantity")}
          />
        </FormField>

        <div className="mt-auto flex gap-2 pt-4">
          <Button
            type="button"
            variant="outline"
            className="flex-1"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="flex-1"
            disabled={isMutating || isUploading}
          >
            {editingBus ? "Save" : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}
