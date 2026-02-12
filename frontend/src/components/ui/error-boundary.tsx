"use client";

import { ErrorBoundary as ReactErrorBoundary } from "react-error-boundary";
import { Suspense, type ReactNode } from "react";
import { RefreshCwIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Text } from "@/components/ui/text";

function ErrorFallback({
  error,
  resetErrorBoundary,
  fallbackMessage,
}: {
  error: unknown;
  resetErrorBoundary: () => void;
  fallbackMessage?: string;
}) {
  const message =
    error instanceof Error && error.message
      ? error.message
      : "Something went wrong";

  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-3 text-center">
      <Text role="muted">
        {fallbackMessage ?? "Something went wrong."} {message}
      </Text>
      <div>
        <Button
          variant="outline"
          size="icon-sm"
          onClick={resetErrorBoundary}
          aria-label="Try again"
        >
          <RefreshCwIcon />
        </Button>
      </div>
    </div>
  );
}

type AsyncBoundaryProps = {
  children: ReactNode;
  suspenseKey?: string;
  fallback?: ReactNode;
  onReset: () => void;
  fallbackMessage?: string;
};

export function AsyncBoundary({
  children,
  suspenseKey,
  fallback,
  onReset,
  fallbackMessage,
}: AsyncBoundaryProps) {
  return (
    <ReactErrorBoundary
      onReset={onReset}
      fallbackRender={({ error, resetErrorBoundary }) => (
        <ErrorFallback
          error={error}
          resetErrorBoundary={resetErrorBoundary}
          fallbackMessage={fallbackMessage}
        />
      )}
    >
      <Suspense key={suspenseKey} fallback={fallback}>
        {children}
      </Suspense>
    </ReactErrorBoundary>
  );
}
