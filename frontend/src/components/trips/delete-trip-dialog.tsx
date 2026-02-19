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
import type { TripReadAdmin } from "@/generated/api/model";

type DeleteTripDialogProps = {
  trip: TripReadAdmin | null;
  onConfirm: () => void;
  onCancel: () => void;
  disabled: boolean;
};

export function DeleteTripDialog({
  trip,
  onConfirm,
  onCancel,
  disabled,
}: DeleteTripDialogProps) {
  return (
    <AlertDialog open={!!trip} onOpenChange={(open) => !open && onCancel()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete trip</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete this trip (
            {trip?.trip_stops.length ?? 0} stops, $
            {trip?.price_per_seat.toFixed(2)}/seat)? This action cannot be
            undone.
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
