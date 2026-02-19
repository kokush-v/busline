import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function BookingWizardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Step indicator skeleton */}
      <div className="flex items-center justify-center gap-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            {i > 0 && <Skeleton className="h-px w-12" />}
            <div className="flex flex-col items-center gap-1">
              <Skeleton className="size-8 rounded-full" />
              <Skeleton className="h-3 w-16" />
            </div>
          </div>
        ))}
      </div>

      {/* Content card skeleton */}
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-2/3" />
          <Skeleton className="mt-2 h-4 w-1/3" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-1/3" />
        </CardContent>
      </Card>
    </div>
  );
}
