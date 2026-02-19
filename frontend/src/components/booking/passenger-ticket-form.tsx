import type { UseFormRegister, FieldErrors } from "react-hook-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { FormField } from "@/components/ui/form-field";
import type { BookingFormValues } from "./types";

type PassengerTicketFormProps = {
  index: number;
  positionIndex: number;
  register: UseFormRegister<BookingFormValues>;
  errors: FieldErrors<BookingFormValues>;
};

export function PassengerTicketForm({
  index,
  positionIndex,
  register,
  errors,
}: PassengerTicketFormProps) {
  const fieldErrors = errors.passengers?.[index];

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm">
          Seat {positionIndex} — Passenger {index + 1}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <FormField
          id={`passenger-${index}-name`}
          label="Full Name *"
          error={fieldErrors?.passenger_name?.message}
        >
          <Input
            id={`passenger-${index}-name`}
            placeholder="John Doe"
            {...register(`passengers.${index}.passenger_name`)}
          />
        </FormField>

        <FormField
          id={`passenger-${index}-email`}
          label="Email"
          error={fieldErrors?.passenger_email?.message}
        >
          <Input
            id={`passenger-${index}-email`}
            type="email"
            placeholder="john@example.com"
            {...register(`passengers.${index}.passenger_email`)}
          />
        </FormField>

        <FormField
          id={`passenger-${index}-age`}
          label="Age"
          error={fieldErrors?.passenger_age?.message}
        >
          <Input
            id={`passenger-${index}-age`}
            type="number"
            placeholder="25"
            min={1}
            max={150}
            {...register(`passengers.${index}.passenger_age`)}
          />
        </FormField>
      </CardContent>
    </Card>
  );
}
