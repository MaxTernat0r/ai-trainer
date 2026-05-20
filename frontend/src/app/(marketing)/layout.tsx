import type { ReactNode } from "react";

export default function MarketingLayout({ children }: { children: ReactNode }) {
  return <main className="min-h-dvh">{children}</main>;
}
