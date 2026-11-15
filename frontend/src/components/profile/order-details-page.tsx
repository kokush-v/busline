"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSuspenseQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowRightIcon, DownloadIcon, Loader2Icon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Spinner } from "@/components/ui/spinner";
import { Text } from "@/components/ui/text";
import { TripStopTimeline } from "@/components/public-trips/trip-stop-timeline";
import { routes } from "@/lib/routes";
import { getErrorMessage } from "@/lib/api/error-handler";
import { AXIOS_INSTANCE } from "@/lib/api/http-instance";
import { getAccessToken } from "@/utils/auth";
import {
  getOrder,
  getGetOrderQueryKey,
  getOrderTickets,
  getGetOrderTicketsQueryKey,
  usePostPayOrder,
  useDeleteCancelOrder,
} from "@/generated/api/endpoints/orders/orders";
import {
  getTripPublic,
  getGetTripPublicQueryKey,
} from "@/generated/api/endpoints/trips/trips";
import type { OrderStatus } from "@/generated/api/model";

const statusBadgeVariant: Record<
  OrderStatus,
  "success" | "warning" | "destructive"
> = {
  PAID: "success",
  PENDING: "warning",
  PROCESSING: "warning",
  FAILED: "destructive",
  CANCELLED: "destructive",
};

type OrderDetailsPageProps = {
  orderId: string;
};

export function OrderDetailsPage({ orderId }: OrderDetailsPageProps) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: order } = useSuspenseQuery({
    queryKey: getGetOrderQueryKey(orderId),
    queryFn: () => getOrder(orderId),
  });

  const { data: tickets } = useSuspenseQuery({
    queryKey: getGetOrderTicketsQueryKey(orderId),
    queryFn: () => getOrderTickets(orderId),
  });

  const tripId = tickets[0]?.trip_id;

  const invalidateOrder = () => {
    queryClient.invalidateQueries({ queryKey: getGetOrderQueryKey(orderId) });
    queryClient.invalidateQueries({ queryKey: ["user-orders"] });
  };

  const payMutation = usePostPayOrder({
    mutation: {
      onSuccess: () => {
        toast.success("Payment successful");
        invalidateOrder();
      },
      onError: (error) => toast.error(getErrorMessage(error)),
    },
  });

  const cancelMutation = useDeleteCancelOrder({
    mutation: {
      onSuccess: () => {
        toast.success("Order cancelled");
        invalidateOrder();
        router.push(routes.profile);
      },
      onError: (error) => toast.error(getErrorMessage(error)),
    },
  });

  const canPay = order.status === "PENDING" || order.status === "PROCESSING";
  const canCancel = order.status === "PENDING";
  const isLoading = payMutation.isPending || cancelMutation.isPending;

  return (
    <div className="mx-auto w-full max-w-[80%] space-y-6 pt-6">
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Order info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              Order — {orderId.slice(0, 8)}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex flex-wrap items-center gap-3">
              <Badge variant={statusBadgeVariant[order.status]}>
                {order.status}
              </Badge>
              <Text role="date">{order.created_at}</Text>
            </div>
            <Text className="text-lg font-semibold">₴{order.total_price}</Text>
            {order.status === "PENDING" && order.expires_at && (
              <Text role="muted">
                Expires: <Text role="date">{order.expires_at}</Text>
              </Text>
            )}
          </CardContent>
        </Card>

        {/* Trip route */}
        {tripId && <TripRouteCard tripId={tripId} />}
      </div>

      {/* Tickets */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Tickets</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {tickets.length === 0 ? (
            <Text role="muted">No tickets in this order.</Text>
          ) : (
            tickets.map((ticket) => (
              <div
                key={ticket.id}
                className="bg-muted/50 flex items-center justify-between rounded-md px-3 py-2"
              >
                <div className="flex flex-col gap-0.5">
                  <Text role="p-sm" className="font-medium">
                    {ticket.passenger_name}
                  </Text>
                  <Text role="muted-xs">
                    Seat: {ticket.seat_id.slice(0, 8)}
                  </Text>
                </div>
                <div className="flex items-center gap-3">
                  <Text role="p-sm" className="font-semibold">
                    ₴{ticket.price}
                  </Text>
                  <TicketPdfButton
                    ticketId={ticket.id}
                    pdfStatus={ticket.pdf_status}
                    passengerName={ticket.passenger_name}
                  />
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      {(canPay || canCancel) && (
        <>
          <Separator />
          <div className="flex gap-2">
            {canPay && (
              <Button
                disabled={isLoading}
                onClick={() => payMutation.mutate({ orderId })}
              >
                {payMutation.isPending && <Spinner />}
                Pay
              </Button>
            )}
            {canCancel && (
              <Button
                variant="destructive"
                disabled={isLoading}
                onClick={() => cancelMutation.mutate({ orderId })}
              >
                {cancelMutation.isPending && <Spinner />}
                Cancel
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function TicketPdfButton({
  ticketId,
  pdfStatus,
  passengerName,
}: {
  ticketId: string;
  pdfStatus?: string;
  passengerName: string;
}) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const response = await AXIOS_INSTANCE.get(`/tickets/${ticketId}/pdf`, {
        responseType: "blob",
        headers: {
          Authorization: `Bearer ${getAccessToken()}`,
        },
      });
      const url = URL.createObjectURL(response.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ticket-${passengerName.replace(/\s+/g, "-")}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Failed to download PDF");
    } finally {
      setDownloading(false);
    }
  };

  if (pdfStatus === "READY") {
    return (
      <Button
        variant="outline"
        size="icon-sm"
        disabled={downloading}
        onClick={handleDownload}
        aria-label="Download PDF"
      >
        {downloading ? (
          <Loader2Icon className="size-4 animate-spin" />
        ) : (
          <DownloadIcon className="size-4" />
        )}
      </Button>
    );
  }

  if (pdfStatus === "GENERATING" || pdfStatus === "PENDING") {
    return (
      <Button
        variant="outline"
        size="icon-sm"
        disabled
        aria-label="Generating PDF"
      >
        <Loader2Icon className="size-4 animate-spin" />
      </Button>
    );
  }

  return null;
}

function TripRouteCard({ tripId }: { tripId: string }) {
  const { data: trip } = useSuspenseQuery({
    queryKey: getGetTripPublicQueryKey(tripId),
    queryFn: () => getTripPublic(tripId),
  });

  const stops = [...trip.trip_stops].sort(
    (a, b) => a.position_index - b.position_index,
  );
  const fromCity = stops[0]?.stop.city.name ?? "—";
  const toCity = stops[stops.length - 1]?.stop.city.name ?? "—";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          {fromCity}
          <ArrowRightIcon className="size-4 shrink-0" />
          {toCity}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <TripStopTimeline stops={trip.trip_stops} />
      </CardContent>
    </Card>
  );
}
