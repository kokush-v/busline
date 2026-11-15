import { z } from "zod";

export const busFormSchema = z.object({
  number_plate: z.string().min(1, "Number plate is required").max(20),
  color: z.string().min(1, "Color is required"),
  seats_quantity: z.coerce.number().int().min(0, "Must be 0 or more"),
});

export type BusFormValues = z.infer<typeof busFormSchema>;
