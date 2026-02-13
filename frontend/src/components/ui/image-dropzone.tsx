"use client";

import { useCallback, useRef, useState } from "react";
import ReactCrop, { type Crop, type PixelCrop } from "react-image-crop";
import "react-image-crop/dist/ReactCrop.css";
import { ImageIcon, Trash2Icon, UploadIcon, Loader2Icon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { LoadingImage } from "@/components/ui/loading-image";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type ImageDropzoneProps = {
  value: File | null;
  onChange: (file: File | null) => void;
  existingImageUrl?: string | null;
  onDeleteExisting?: () => void;
  isUploading?: boolean;
  isDeleting?: boolean;
  disabled?: boolean;
};

const ACCEPT = "image/jpeg,image/png";

function getCroppedFile(
  image: HTMLImageElement,
  crop: PixelCrop,
  fileName: string,
  mimeType: string,
): Promise<File> {
  const canvas = document.createElement("canvas");
  const scaleX = image.naturalWidth / image.width;
  const scaleY = image.naturalHeight / image.height;
  canvas.width = crop.width * scaleX;
  canvas.height = crop.height * scaleY;
  const ctx = canvas.getContext("2d")!;

  ctx.drawImage(
    image,
    crop.x * scaleX,
    crop.y * scaleY,
    crop.width * scaleX,
    crop.height * scaleY,
    0,
    0,
    canvas.width,
    canvas.height,
  );

  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      resolve(new File([blob!], fileName, { type: mimeType }));
    }, mimeType);
  });
}

export function ImageDropzone({
  value,
  onChange,
  existingImageUrl,
  onDeleteExisting,
  isUploading,
  isDeleting,
  disabled,
}: ImageDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const imgRef = useRef<HTMLImageElement | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  // Crop state
  const [cropSrc, setCropSrc] = useState<string | null>(null);
  const [cropFileName, setCropFileName] = useState("");
  const [cropMimeType, setCropMimeType] = useState("");
  const [crop, setCrop] = useState<Crop>();
  const [completedCrop, setCompletedCrop] = useState<PixelCrop>();

  const previewUrl = value ? URL.createObjectURL(value) : null;
  const displayUrl = previewUrl ?? existingImageUrl;

  const openCropDialog = useCallback((file: File) => {
    const url = URL.createObjectURL(file);
    setCropSrc(url);
    setCropFileName(file.name);
    setCropMimeType(file.type);
    setCrop(undefined);
    setCompletedCrop(undefined);
  }, []);

  const closeCropDialog = useCallback(() => {
    if (cropSrc) URL.revokeObjectURL(cropSrc);
    setCropSrc(null);
  }, [cropSrc]);

  const handleImageLoad = useCallback(
    (e: React.SyntheticEvent<HTMLImageElement>) => {
      imgRef.current = e.currentTarget;
      const { width, height } = e.currentTarget;
      const size = Math.min(width, height);
      const x = (width - size) / 2;
      const y = (height - size) / 2;
      setCrop({ unit: "px", x, y, width: size, height: size });
    },
    [],
  );

  const handleCropConfirm = useCallback(async () => {
    if (!imgRef.current || !completedCrop) return;
    const cropped = await getCroppedFile(
      imgRef.current,
      completedCrop,
      cropFileName,
      cropMimeType,
    );
    closeCropDialog();
    onChange(cropped);
  }, [completedCrop, cropFileName, cropMimeType, closeCropDialog, onChange]);

  const handleFile = useCallback(
    (file: File | null) => {
      if (!file) return;
      if (!file.type.match(/^image\/(jpeg|png)$/)) return;
      openCropDialog(file);
    },
    [openCropDialog],
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!disabled && !isUploading) setIsDragOver(true);
    },
    [disabled, isUploading],
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      if (disabled || isUploading) return;
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [disabled, isUploading, handleFile],
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0] ?? null;
      handleFile(file);
      e.target.value = "";
    },
    [handleFile],
  );

  const handleRemoveClick = useCallback(() => {
    if (value) {
      onChange(null);
      setConfirmDelete(false);
      return;
    }
    if (!existingImageUrl || !onDeleteExisting) return;

    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }

    onDeleteExisting();
    setConfirmDelete(false);
  }, [value, onChange, existingImageUrl, onDeleteExisting, confirmDelete]);

  const hasImage = !!displayUrl;
  const canRemove = hasImage && !isUploading && !isDeleting && !disabled;
  const isExistingImage = !value && !!existingImageUrl;

  return (
    <div className="flex flex-col gap-2">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && !isUploading && inputRef.current?.click()}
        className={cn(
          "relative flex aspect-square cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed transition-colors",
          isDragOver
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-muted-foreground/50",
          (disabled || isUploading) && "cursor-not-allowed opacity-50",
          hasImage && "border-muted border-solid",
        )}
      >
        {isUploading ? (
          <div className="text-muted-foreground flex flex-col items-center gap-2">
            <Loader2Icon className="size-8 animate-spin" />
            <span className="text-xs">Uploading...</span>
          </div>
        ) : hasImage ? (
          <LoadingImage
            key={displayUrl}
            src={displayUrl!}
            alt="Bus photo"
            className="size-full rounded-md"
          />
        ) : (
          <div className="text-muted-foreground flex flex-col items-center gap-2">
            {isDragOver ? (
              <UploadIcon className="size-8" />
            ) : (
              <ImageIcon className="size-8" />
            )}
            <span className="text-xs">
              {isDragOver ? "Drop image here" : "Click or drag image"}
            </span>
            <span className="text-muted-foreground/60 text-[10px]">
              JPG or PNG
            </span>
          </div>
        )}

        {isDeleting && (
          <div className="absolute inset-0 flex items-center justify-center rounded-md bg-black/40">
            <Loader2Icon className="size-6 animate-spin text-white" />
          </div>
        )}

        {canRemove &&
          (confirmDelete && isExistingImage ? (
            <div
              className="bg-destructive/90 absolute inset-x-0 bottom-0 flex items-center justify-between rounded-b-md px-3 py-1.5"
              onClick={(e) => e.stopPropagation()}
            >
              <span className="text-xs font-medium text-white">
                Delete photo?
              </span>
              <div className="flex gap-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="xs"
                  className="text-white hover:bg-white/20"
                  onClick={() => setConfirmDelete(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="xs"
                  className="text-white hover:bg-white/20"
                  onClick={handleRemoveClick}
                >
                  Delete
                </Button>
              </div>
            </div>
          ) : (
            <Button
              type="button"
              variant="destructive"
              size="icon-xs"
              className="absolute top-1.5 right-1.5"
              onClick={(e) => {
                e.stopPropagation();
                handleRemoveClick();
              }}
            >
              <Trash2Icon />
            </Button>
          ))}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="hidden"
        onChange={handleInputChange}
        disabled={disabled || isUploading}
      />

      <Dialog
        open={!!cropSrc}
        onOpenChange={(open) => !open && closeCropDialog()}
      >
        <DialogContent showCloseButton={false} className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Crop Image</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center">
            {cropSrc && (
              <ReactCrop
                crop={crop}
                onChange={setCrop}
                onComplete={setCompletedCrop}
                aspect={1}
                className="max-h-[60vh]"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={cropSrc}
                  alt="Crop preview"
                  onLoad={handleImageLoad}
                  className="max-h-[60vh] object-contain"
                />
              </ReactCrop>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeCropDialog}>
              Cancel
            </Button>
            <Button onClick={handleCropConfirm} disabled={!completedCrop}>
              Confirm
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
