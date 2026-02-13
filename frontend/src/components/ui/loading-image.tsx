"use client";

import { useState } from "react";
import { Loader2Icon } from "lucide-react";
import { cn } from "@/lib/utils";

type LoadingImageProps = Omit<
  React.ComponentProps<"img">,
  "onLoad" | "onError"
> & {
  fallback?: React.ReactNode;
};

export function LoadingImage({
  className,
  fallback,
  src,
  ...props
}: LoadingImageProps) {
  const [status, setStatus] = useState<"loading" | "loaded" | "error">(
    "loading",
  );

  if (!src) return fallback ?? null;

  return (
    <div className={cn("relative overflow-hidden", className)}>
      {status === "loading" && (
        <div className="text-muted-foreground absolute inset-0 flex items-center justify-center">
          <Loader2Icon className="size-6 animate-spin" />
        </div>
      )}
      {status === "error" ? (
        (fallback ?? null)
      ) : (
        /* eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text */
        <img
          src={src}
          className={cn(
            "size-full object-cover transition-opacity",
            status === "loaded" ? "opacity-100" : "opacity-0",
          )}
          onLoad={() => setStatus("loaded")}
          onError={() => setStatus("error")}
          {...props}
        />
      )}
    </div>
  );
}
