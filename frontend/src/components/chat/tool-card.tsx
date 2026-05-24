'use client';

import { CheckCircle2, Loader2, XCircle, Wrench } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ToolCardProps {
  summary: string;
  state: 'running' | 'ok' | 'error';
  className?: string;
}

/**
 * Inline read-only tool card. Shown while the agent is consulting data
 * (get_profile, list_workout_plans, ...) and after it finishes.
 */
export function ToolCard({ summary, state, className }: ToolCardProps) {
  const Icon = state === 'running' ? Loader2 : state === 'ok' ? CheckCircle2 : XCircle;
  return (
    <div
      className={cn(
        'glass-lane mt-2 inline-flex max-w-full items-center gap-2 rounded-lg border px-3 py-1.5 text-xs',
        state === 'error'
          ? 'border-destructive/40 text-destructive'
          : state === 'ok'
            ? 'border-primary/30 text-foreground/85'
            : 'border-primary/20 text-muted-foreground',
        className,
      )}
    >
      {state === 'running' ? (
        <Icon className="size-3.5 animate-spin" />
      ) : (
        <Icon className="size-3.5" />
      )}
      <Wrench className="size-3 opacity-60" />
      <span className="truncate">{summary}</span>
    </div>
  );
}
