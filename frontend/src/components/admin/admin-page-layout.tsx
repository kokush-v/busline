"use client";

import { useState, type ReactNode } from "react";
import { cn } from "@/lib/utils";

type AdminPageLayoutProps = {
  children: ReactNode;
  panel?: ReactNode;
};

export function AdminPageLayout({ children, panel }: AdminPageLayoutProps) {
  const hasPanel = !!panel;
  const [prevHasPanel, setPrevHasPanel] = useState(false);
  const [cachedPanel, setCachedPanel] = useState<ReactNode>(null);
  const [closing, setClosing] = useState(false);

  // Derived state during render (React-approved pattern)
  if (hasPanel && !prevHasPanel) {
    setPrevHasPanel(true);
    setCachedPanel(panel);
    setClosing(false);
  } else if (!hasPanel && prevHasPanel) {
    setPrevHasPanel(false);
    setClosing(true);
  }

  const handleTransitionEnd = () => {
    if (closing) {
      setClosing(false);
      setCachedPanel(null);
    }
  };

  const showContent = hasPanel || closing;
  const renderedPanel = hasPanel ? panel : cachedPanel;

  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-1 gap-6">
      <div className="flex min-w-0 flex-1 flex-col gap-6">{children}</div>
      <div
        className={cn(
          "shrink-0 self-stretch transition-[width,opacity] duration-200 ease-out",
          hasPanel ? "w-96 opacity-100" : "w-0 opacity-0",
        )}
        onTransitionEnd={handleTransitionEnd}
      >
        {showContent && (
          <div
            className={cn(
              "flex h-full",
              hasPanel &&
                !closing &&
                "animate-in slide-in-from-right fade-in duration-200",
            )}
          >
            {renderedPanel}
          </div>
        )}
      </div>
    </div>
  );
}
