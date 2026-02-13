import type { ReactNode } from "react";

type AdminPageLayoutProps = {
  children: ReactNode;
  panel?: ReactNode;
};

export function AdminPageLayout({ children, panel }: AdminPageLayoutProps) {
  return (
    <div className="flex min-h-[calc(100vh-8rem)] flex-1 gap-6">
      <div className="flex min-w-0 flex-1 flex-col gap-6">{children}</div>
      {panel}
    </div>
  );
}
