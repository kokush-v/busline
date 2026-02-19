"use client";

import { useSuspenseQuery } from "@tanstack/react-query";
import { SearchXIcon } from "lucide-react";
import { Text } from "@/components/ui/text";
import { Pagination } from "@/components/ui/pagination";
import {
  getTripsPublic,
  getGetTripsPublicQueryKey,
} from "@/generated/api/endpoints/trips/trips";
import type { GetTripsPublicParams } from "@/generated/api/model";
import { TripCard } from "./trip-card";

type TripCardListProps = {
  params: GetTripsPublicParams;
  onOffsetChange: (offset: number) => void;
};

export function TripCardList({ params, onOffsetChange }: TripCardListProps) {
  const { data } = useSuspenseQuery({
    queryKey: getGetTripsPublicQueryKey(params),
    queryFn: () => getTripsPublic(params),
  });

  if (!data.items.length) {
    return (
      <div className="text-muted-foreground flex flex-col items-center gap-2 py-16 text-center">
        <SearchXIcon className="size-8" />
        <Text role="muted">No trips found.</Text>
        <Text role="muted-xs">Try adjusting your filters.</Text>
      </div>
    );
  }

  const limit = params.limit ?? 12;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data.items.map((trip) => (
          <TripCard key={trip.id} trip={trip} />
        ))}
      </div>

      {data.total > limit && (
        <Pagination
          offset={params.offset ?? 0}
          limit={limit}
          total={data.total}
          onPrevious={() =>
            onOffsetChange(Math.max(0, (params.offset ?? 0) - limit))
          }
          onNext={() => onOffsetChange((params.offset ?? 0) + limit)}
          onPageChange={(page) => onOffsetChange((page - 1) * limit)}
        />
      )}
    </div>
  );
}
