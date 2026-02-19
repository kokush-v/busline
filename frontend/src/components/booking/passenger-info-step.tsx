"use client";

import { useForm, useFieldArray } from "react-hook-form";
import { standardSchemaResolver } from "@hookform/resolvers/standard-schema";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Spinner } from "@/components/ui/spinner";
import { usePostReserveSeats } from "@/generated/api/endpoints/seats/seats";
import { getErrorMessage } from "@/lib/api/error-handler";
import type { ReserveSeatResponse } from "@/generated/api/model";
import { bookingFormSchema, type BookingFormValues } from "./types";
import { PassengerTicketForm } from "./passenger-ticket-form";

type PassengerInfoStepProps = {
  tripId: string;
  startStopId: string;
  finishStopId: string;
  selectedSeats: { id: string; position_index: number }[];
  pricePerSeat: number;
  onBack: () => void;
  onSuccess: (order: ReserveSeatResponse) => void;
};

export function PassengerInfoStep({
  tripId,
  startStopId,
  finishStopId,
  selectedSeats,
  pricePerSeat,
  onBack,
  onSuccess,
}: PassengerInfoStepProps) {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<BookingFormValues>({
    resolver: standardSchemaResolver(bookingFormSchema),
    defaultValues: {
      passengers: selectedSeats.map((seat) => ({
        seat_id: seat.id,
        position_index: seat.position_index,
        passenger_name: "",
        passenger_email: "",
        passenger_age: "",
      })),
    },
  });

  const { fields } = useFieldArray({
    control,
    name: "passengers",
  });

  const { mutate: reserveSeats, isPending } = usePostReserveSeats();

  const totalPrice = selectedSeats.length * pricePerSeat;

  const onSubmit = (data: BookingFormValues) => {
    reserveSeats(
      {
        data: {
          trip_id: tripId,
          tickets: data.passengers.map((p) => ({
            seat_id: p.seat_id,
            passenger_name: p.passenger_name,
            passenger_email: p.passenger_email || null,
            passenger_age:
              p.passenger_age !== "" && p.passenger_age !== undefined
                ? Number(p.passenger_age)
                : null,
            start_stop_id: startStopId,
            finish_stop_id: finishStopId,
          })),
        },
      },
      {
        onSuccess: (order) => {
          toast.success("Reservation confirmed!");
          onSuccess(order);
        },
        onError: (error) => {
          toast.error(getErrorMessage(error));
        },
      },
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Tabs defaultValue="0">
        <TabsList className="w-full">
          {fields.map((field, index) => (
            <TabsTrigger key={field.id} value={String(index)}>
              Seat {selectedSeats[index].position_index}
            </TabsTrigger>
          ))}
        </TabsList>
        {fields.map((field, index) => (
          <TabsContent
            key={field.id}
            value={String(index)}
            className="animate-in fade-in-0 duration-300"
          >
            <PassengerTicketForm
              index={index}
              positionIndex={selectedSeats[index].position_index}
              register={register}
              errors={errors}
            />
          </TabsContent>
        ))}
      </Tabs>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Price Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="text-muted-foreground flex justify-between text-sm">
            <span>
              {selectedSeats.length} seat(s) x {pricePerSeat} UAH
            </span>
            <span>{totalPrice} UAH</span>
          </div>
          <Separator />
          <div className="flex justify-between font-semibold">
            <span>Total</span>
            <span>{totalPrice} UAH</span>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-between">
        <Button
          type="button"
          variant="outline"
          onClick={onBack}
          disabled={isPending}
        >
          Back
        </Button>
        <Button type="submit" disabled={isPending}>
          {isPending && <Spinner className="mr-2 size-4" />}
          Reserve
        </Button>
      </div>
    </form>
  );
}
