import type { BusRead } from "@/generated/api/model";
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

type DeleteBusDialogProps = {
  bus: BusRead | null;
  onConfirm: () => void;
  onCancel: () => void;
  disabled: boolean;
};

export function DeleteBusDialog({
  bus,
  onConfirm,
  onCancel,
  disabled,
}: DeleteBusDialogProps) {
  return (
    <AlertDialog open={!!bus} onOpenChange={(open) => !open && onCancel()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete bus</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete &quot;{bus?.number_plate}&quot;?
            This action cannot be undone.
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
