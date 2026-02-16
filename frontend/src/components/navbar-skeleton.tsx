import { Skeleton } from "@/components/ui/skeleton";

export function NavbarSkeleton() {
  return (
    <nav className="bg-background sticky top-0 z-50 border-b">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Skeleton className="h-8 w-24" />
        <Skeleton className="h-10 w-20" />
      </div>
    </nav>
  );
}
