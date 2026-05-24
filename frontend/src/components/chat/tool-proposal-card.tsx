'use client';

import { CheckCircle2, Loader2, XCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { ToolProposal } from '@/types/chat';

interface ToolProposalCardProps {
  proposal: ToolProposal;
  disabled?: boolean;
  onApprove: () => void;
  onReject: () => void;
}

const TOOL_LINK_AFTER_APPROVE: Record<string, string> = {
  generate_workout_plan: '/workouts',
  generate_nutrition_plan: '/nutrition',
  schedule_workout_plan: '/workouts',
  log_food: '/nutrition',
  log_weight: '/analytics',
  log_measurement: '/analytics',
  log_exercise_set: '/workouts',
  activate_workout_plan: '/workouts',
  activate_nutrition_plan: '/nutrition',
  update_profile: '/profile',
  add_medical_restriction: '/profile',
};

export function ToolProposalCard({
  proposal,
  disabled,
  onApprove,
  onReject,
}: ToolProposalCardProps) {
  const link = TOOL_LINK_AFTER_APPROVE[proposal.name];

  if (proposal.status === 'pending') {
    return (
      <div className="cockpit-panel mt-3 flex flex-col gap-3 rounded-xl p-3 text-sm">
        <div className="flex items-start gap-2 text-foreground/90">
          <span
            className="mt-1.5 inline-block size-2 shrink-0 rounded-full bg-primary"
            aria-hidden
          />
          <p className="font-medium">{proposal.summary}</p>
        </div>
        <p className="text-xs text-muted-foreground">
          ИИ предлагает выполнить это действие. Подтвердите, чтобы оно применилось.
        </p>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            size="sm"
            className="priority-action"
            disabled={disabled}
            onClick={onApprove}
          >
            Применить
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={disabled}
            onClick={onReject}
          >
            Отменить
          </Button>
        </div>
      </div>
    );
  }

  if (proposal.status === 'executing') {
    return (
      <div className="glass-lane mt-3 flex items-center gap-2 rounded-lg border border-primary/30 px-3 py-2 text-xs">
        <Loader2 className="size-3.5 animate-spin" />
        <span>Выполняю: {proposal.summary}</span>
      </div>
    );
  }

  if (proposal.status === 'approved') {
    return (
      <div className="glass-lane mt-3 flex flex-wrap items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 px-3 py-2 text-xs">
        <CheckCircle2 className="size-3.5 text-primary" />
        <span className="text-foreground/90">{proposal.resultSummary || 'Готово'}</span>
        {link && (
          <Link
            href={link}
            className="ml-auto inline-flex items-center gap-1 text-primary hover:underline"
          >
            Открыть
            <ArrowRight className="size-3" />
          </Link>
        )}
      </div>
    );
  }

  if (proposal.status === 'rejected') {
    return (
      <div
        className={cn(
          'glass-lane mt-3 flex items-center gap-2 rounded-lg border px-3 py-2 text-xs',
          'border-muted-foreground/30 text-muted-foreground',
        )}
      >
        <XCircle className="size-3.5" />
        <span>Действие отменено</span>
      </div>
    );
  }

  // error
  return (
    <div className="glass-lane mt-3 flex items-start gap-2 rounded-lg border border-destructive/40 px-3 py-2 text-xs text-destructive">
      <XCircle className="size-3.5 mt-0.5 shrink-0" />
      <span>{proposal.error || 'Не удалось выполнить'}</span>
    </div>
  );
}
