'use client';

import { Dumbbell } from 'lucide-react';
import Link from 'next/link';

export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="flex h-16 items-center border-b border-border px-4">
        <Link href="/" className="flex items-center gap-2">
          <Dumbbell className="size-6 text-primary" />
          <span className="text-lg font-bold">AI Trainer</span>
        </Link>
      </header>
      <main className="flex flex-1 items-start justify-center px-4 py-8 sm:py-12">
        <div className="w-full max-w-2xl">{children}</div>
      </main>
    </div>
  );
}
