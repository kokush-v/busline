import { NavbarSkeleton } from "@/components/navbar-skeleton";
import { Spinner } from "@/components/ui/spinner";

export function PageSkeleton() {
  return (
    <>
      <NavbarSkeleton />
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <Spinner className="size-8" />
      </div>
    </>
  );
}
