import type { CityRead } from "@/generated/api/model";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

type DeleteCityDialogProps = {
  city: CityRead | null;
  onConfirm: () => void;
  onCancel: () => void;
  disabled: boolean;
};

export function DeleteCityDialog({
  city,
  onConfirm,
  onCancel,
  disabled,
}: DeleteCityDialogProps) {
  return (
    <AlertDialog open={!!city} onOpenChange={(open) => !open && onCancel()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete city</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete &quot;{city?.name}&quot;? This
            action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} disabled={disabled}>
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
