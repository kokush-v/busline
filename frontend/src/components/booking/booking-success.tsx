import Link from "next/link";
import { CheckCircle2Icon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { routes } from "@/lib/routes";
import type { BookingSuccessData } from "./types";

type BookingSuccessProps = {
  order: BookingSuccessData;
  tripId: string;
};

export function BookingSuccess({ order, tripId }: BookingSuccessProps) {
  return (
    <Card>
      <CardContent className="space-y-4 pt-6 text-center">
        <div className="flex justify-center">
          <CheckCircle2Icon className="text-primary size-16" />
        </div>
        <h2 className="text-2xl font-bold">Reservation Confirmed!</h2>

        <div className="text-muted-foreground space-y-1 text-sm">
          <p>
            Order ID:{" "}
            <span className="text-foreground font-mono">{order.id}</span>
          </p>
          <p>
            Status:{" "}
            <span className="text-foreground font-medium">{order.status}</span>
          </p>
          <p>
            Total:{" "}
            <span className="text-foreground font-semibold">
              {order.total_price} UAH
            </span>
          </p>
          {order.expires_at && (
            <p>
              Expires:{" "}
              <span className="text-foreground">
                {new Date(order.expires_at).toLocaleString("en-GB", {
                  day: "numeric",
                  month: "short",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </p>
          )}
          <p>
            Tickets:{" "}
            <span className="text-foreground">{order.tickets.length}</span>
          </p>
        </div>

        <Separator />

        <div className="flex justify-center gap-3">
          <Button asChild variant="outline">
            <Link href={routes.tripDetails(tripId)}>View Trip</Link>
          </Button>
          <Button asChild>
            <Link href={routes.trips}>Back to Trips</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
