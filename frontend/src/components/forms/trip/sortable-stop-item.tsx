import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { XIcon, GripVerticalIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import type { SortableStopItemProps } from "./types";

export function SortableStopItem({
  field,
  index,
  stopName,
  onRemove,
  register,
  errors,
}: SortableStopItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: field.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="bg-muted/40 rounded-md border p-3"
    >
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="text-muted-foreground hover:text-foreground cursor-grab touch-none active:cursor-grabbing"
            {...attributes}
            {...listeners}
          >
            <GripVerticalIcon className="size-4" />
          </button>
          <span className="text-sm font-medium">
            #{index + 1} {stopName}
          </span>
        </div>
        <Button type="button" variant="ghost" size="icon-sm" onClick={onRemove}>
          <XIcon className="size-3" />
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <FormField
          id={`stop-${index}-arrival`}
          label="Arrival"
          error={errors.stops?.[index]?.arrival_time?.message}
        >
          <Input
            id={`stop-${index}-arrival`}
            type="datetime-local"
            {...register(`stops.${index}.arrival_time`)}
          />
        </FormField>
        <FormField
          id={`stop-${index}-departure`}
          label="Departure"
          error={errors.stops?.[index]?.departure_time?.message}
        >
          <Input
            id={`stop-${index}-departure`}
            type="datetime-local"
            {...register(`stops.${index}.departure_time`)}
          />
        </FormField>
      </div>
    </div>
  );
}
