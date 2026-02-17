import { z } from "zod";

export const tripFormSchema = z.object({
  bus_id: z.string().min(1, "Bus is required"),
  price_per_seat: z.coerce.number().min(0, "Price must be 0 or more"),
  stops: z
    .array(
      z.object({
        stop_id: z.string(),
        arrival_time: z.string().min(1, "Arrival time is required"),
        departure_time: z.string().min(1, "Departure time is required"),
      }),
    )
    .min(2, "At least 2 stops are required"),
});

export type TripFormValues = z.infer<typeof tripFormSchema>;
