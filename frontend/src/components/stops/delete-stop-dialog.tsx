import type { StopRead } from "@/generated/api/model";
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

type DeleteStopDialogProps = {
  stop: StopRead | null;
  onConfirm: () => void;
  onCancel: () => void;
  disabled: boolean;
};

export function DeleteStopDialog({
  stop,
  onConfirm,
  onCancel,
  disabled,
}: DeleteStopDialogProps) {
  return (
    <AlertDialog open={!!stop} onOpenChange={(open) => !open && onCancel()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete stop</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete &quot;{stop?.name}&quot;? This
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
