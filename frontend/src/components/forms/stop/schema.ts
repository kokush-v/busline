import { z } from "zod";

export const stopFormSchema = z.object({
  city_id: z.string().min(1, "City is required"),
  name: z.string().min(1, "Stop name is required"),
  latitude: z.coerce.number({ error: "Required" }),
  longitude: z.coerce.number({ error: "Required" }),
});

export type StopFormValues = z.infer<typeof stopFormSchema>;
