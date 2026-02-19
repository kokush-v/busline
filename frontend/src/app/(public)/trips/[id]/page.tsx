"use client";

import { use, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { PageContainer } from "@/components/ui/page-container";
import { AsyncBoundary } from "@/components/ui/error-boundary";
import { TripDetails, TripDetailsSkeleton } from "@/components/public-trips";

type TripDetailsPageProps = {
  params: Promise<{ id: string }>;
};

export default function TripDetailsPage({ params }: TripDetailsPageProps) {
  const { id } = use(params);
  const queryClient = useQueryClient();
  const [retryKey, setRetryKey] = useState(0);

  return (
    <PageContainer centered={false}>
      <div className="mx-auto max-w-6xl">
        <AsyncBoundary
          onReset={() => {
            queryClient.removeQueries({
              queryKey: [`/trips/details/${id}`],
            });
            setRetryKey((k) => k + 1);
          }}
          fallbackMessage="Unable to load trip details."
          suspenseKey={`${id}-${retryKey}`}
          fallback={<TripDetailsSkeleton />}
        >
          <TripDetails tripId={id} />
        </AsyncBoundary>
      </div>
    </PageContainer>
  );
}
