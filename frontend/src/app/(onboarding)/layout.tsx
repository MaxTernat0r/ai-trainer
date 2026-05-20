'use client';

import { Dumbbell } from 'lucide-react';
import Link from 'next/link';

export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex min-h-dvh flex-col px-3 py-3 sm:px-6">
      <header className="cockpit-panel mx-auto flex h-16 w-full max-w-5xl items-center rounded-lg px-4">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-lg border border-primary/35 bg-primary/12 text-primary">
            <Dumbbell className="size-5" />
          </div>
          <div>
            <span className="block text-lg font-bold leading-none">Coach AI</span>
            <span className="tactical-readout text-[0.62rem] text-muted-foreground">
              onboarding sequence
            </span>
          </div>
        </Link>
      </header>
      <main className="flex flex-1 items-start justify-center py-6 sm:py-8">
        <div className="w-full max-w-2xl">{children}</div>
      </main>
    </div>
  );
}
