import { cn } from "@/lib/utils";

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
  centered?: boolean;
}

export function PageContainer({
  children,
  className,
  centered = true,
}: PageContainerProps) {
  return (
    <main
      className={cn(
        "bg-background min-h-[calc(100vh-4rem)] px-6 py-12",
        centered && "flex items-center justify-center",
        className,
      )}
    >
      {children}
    </main>
  );
}
