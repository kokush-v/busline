"use client";

import { use, useCallback, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { PageContainer } from "@/components/ui/page-container";
import { AsyncBoundary } from "@/components/ui/error-boundary";
import { BookingWizard, BookingWizardSkeleton } from "@/components/booking";

type BookingPageProps = {
  params: Promise<{ id: string }>;
};

export default function BookingPage({ params }: BookingPageProps) {
  const { id } = use(params);
  const queryClient = useQueryClient();
  const [retryKey, setRetryKey] = useState(0);

  const handleReset = useCallback(() => {
    queryClient.removeQueries({ queryKey: [`/trips/details/${id}`] });
    queryClient.removeQueries({ queryKey: [`/trips/${id}/seats`] });
    setRetryKey((k) => k + 1);
  }, [queryClient, id]);

  return (
    <PageContainer centered={false}>
      <div className="mx-auto max-w-3xl">
        <AsyncBoundary
          onReset={handleReset}
          fallbackMessage="Unable to load booking."
          suspenseKey={`booking-${id}-${retryKey}`}
          fallback={<BookingWizardSkeleton />}
        >
          <BookingWizard tripId={id} />
        </AsyncBoundary>
      </div>
    </PageContainer>
  );
}
