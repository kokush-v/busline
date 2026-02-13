import { z } from "zod";

export const cityFormSchema = z.object({
  name: z.string().min(1, "City name is required"),
  latitude: z.coerce.number({ error: "Required" }),
  longitude: z.coerce.number({ error: "Required" }),
});

export type CityFormValues = z.infer<typeof cityFormSchema>;
