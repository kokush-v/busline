import { z } from "zod";
import type { ReserveSeatResponse } from "@/generated/api/model";

export type BookingStep = 1 | 2 | 3 | "success";

export const passengerSchema = z.object({
  seat_id: z.string(),
  position_index: z.number(),
  passenger_name: z.string().min(1, "Name is required").max(100),
  passenger_email: z
    .string()
    .email("Invalid email")
    .optional()
    .or(z.literal("")),
  passenger_age: z.coerce
    .number()
    .int()
    .min(1, "Age must be at least 1")
    .max(150, "Invalid age")
    .optional()
    .or(z.literal("")),
});

export const bookingFormSchema = z.object({
  passengers: z.array(passengerSchema).min(1),
});

export type PassengerInfo = z.infer<typeof passengerSchema>;
export type BookingFormValues = z.infer<typeof bookingFormSchema>;

export type BookingSuccessData = ReserveSeatResponse;
