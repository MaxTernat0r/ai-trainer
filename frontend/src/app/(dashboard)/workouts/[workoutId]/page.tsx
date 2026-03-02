'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  ArrowRight,
  Clock,
  CheckCircle2,
  Timer,
  Dumbbell,
  Loader2,
  Play,
  Pause,
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import {
  useWorkoutPlan,
  useLogSet,
  useStartWorkout,
  useToggleComplete,
} from '@/lib/queries/use-workouts';
import type { WorkoutSession } from '@/types/workout';

function formatTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

interface SetEntry {
  setNumber: number;
  reps: string;
  weight: string;
  completed: boolean;
}

// ─── Plan Overview (read-only) ───────────────────────────────────────────────

function PlanOverview({ planId }: { planId: string }) {
  const { data: plan, isLoading } = useWorkoutPlan(planId);

  if (isLoading || !plan) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center gap-3">
          <Skeleton className="size-10 rounded-md" />
          <Skeleton className="h-6 w-2/3" />
        </div>
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i} className="border-border/50">
            <CardHeader><Skeleton className="h-5 w-48" /></CardHeader>
            <CardContent>
              <div className="flex flex-col gap-2">
                {Array.from({ length: 4 }).map((__, j) => (
                  <Skeleton key={j} className="h-10 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/workouts">
            <ArrowLeft className="size-5" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-xl font-bold tracking-tight sm:text-2xl">
            {plan.title}
          </h1>
          {plan.description && (
            <p className="mt-1 text-sm text-muted-foreground">{plan.description}</p>
          )}
        </div>
      </div>

      {/* Sessions with exercises */}
      {plan.sessions.map((session) => (
        <Card key={session.id} className="border-border/50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant="secondary">День {session.day_number}</Badge>
                <CardTitle className="text-base">{session.name}</CardTitle>
              </div>
              <span className="text-xs text-muted-foreground">
                {session.exercises.length} упр.
              </span>
            </div>
            {session.notes && (
              <p className="mt-1 text-sm text-muted-foreground">{session.notes}</p>
            )}
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-2">
              {session.exercises.map((exercise, idx) => (
                <div
                  key={exercise.id}
                  className="flex items-center gap-3 rounded-lg border border-border/50 px-4 py-3"
                >
                  <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium">
                    {idx + 1}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">
                      {exercise.exercise_name_ru ?? exercise.exercise_name ?? 'Упражнение'}
                    </p>
                    {exercise.notes && (
                      <p className="mt-0.5 text-xs text-muted-foreground truncate">{exercise.notes}</p>
                    )}
                  </div>
                  <span className="shrink-0 text-sm text-muted-foreground">
                    {exercise.target_sets}&times;{exercise.target_reps}
                  </span>
                  {exercise.target_rest_seconds && (
                    <span className="shrink-0 text-xs text-muted-foreground">
                      отдых {exercise.target_rest_seconds}с
                    </span>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}

      <Button variant="outline" asChild className="self-start">
        <Link href="/workouts">
          <ArrowLeft className="size-4" />
          Назад к тренировкам
        </Link>
      </Button>
    </div>
  );
}

// ─── Active Workout Session ──────────────────────────────────────────────────

function WorkoutSessionView({
  planId,
  sessionId,
  entryId,
}: {
  planId: string;
  sessionId: string;
  entryId: string;
}) {
  const router = useRouter();
  const { data: plan, isLoading: planLoading } = useWorkoutPlan(planId, entryId);
  const logSetMutation = useLogSet();
  const toggleCompleteMutation = useToggleComplete();

  const session: WorkoutSession | undefined = plan
    ? plan.sessions.find((s) => s.id === sessionId) ?? plan.sessions[0]
    : undefined;

  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [restTimer, setRestTimer] = useState(0);
  const [setEntries, setSetEntries] = useState<SetEntry[]>([]);
  const [initialized, setInitialized] = useState(false);

  // Initialize sets for the current exercise
  const initExerciseSets = useCallback(
    (exerciseIdx: number) => {
      if (!session) return;
      const exercise = session.exercises[exerciseIdx];
      if (!exercise) return;

      const sets: SetEntry[] = [];
      exercise.logged_sets.forEach((ls) => {
        sets.push({
          setNumber: ls.set_number,
          reps: ls.reps_completed?.toString() ?? '',
          weight: ls.weight_kg?.toString() ?? '',
          completed: true,
        });
      });
      for (let i = sets.length; i < exercise.target_sets; i++) {
        sets.push({ setNumber: i + 1, reps: '', weight: '', completed: false });
      }
      setSetEntries(sets);
    },
    [session]
  );

  // Init on session load
  useEffect(() => {
    if (session && !initialized) {
      let startIdx = 0;
      for (let i = 0; i < session.exercises.length; i++) {
        const ex = session.exercises[i];
        if (ex.logged_sets.length < ex.target_sets) {
          startIdx = i;
          break;
        }
      }
      setCurrentExerciseIndex(startIdx);
      setInitialized(true);
    }
  }, [session, initialized]);

  // Re-init sets when exercise changes
  useEffect(() => {
    if (session && initialized) {
      initExerciseSets(currentExerciseIndex);
    }
  }, [currentExerciseIndex, session, initialized, initExerciseSets]);

  // Workout timer
  useEffect(() => {
    if (!isTimerRunning) return;
    const interval = setInterval(() => setElapsedTime((p) => p + 1), 1000);
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  // Rest timer countdown
  useEffect(() => {
    if (restTimer <= 0) return;
    const interval = setInterval(() => setRestTimer((p) => Math.max(0, p - 1)), 1000);
    return () => clearInterval(interval);
  }, [restTimer]);

  const updateSet = (setIndex: number, field: 'reps' | 'weight', value: string) => {
    setSetEntries((prev) => {
      const next = [...prev];
      next[setIndex] = { ...next[setIndex], [field]: value };
      return next;
    });
  };

  const completeSet = (setIndex: number) => {
    if (!session) return;
    const exercise = session.exercises[currentExerciseIndex];
    if (!exercise) return;
    const set = setEntries[setIndex];
    if (!set) return;

    if (!isTimerRunning) setIsTimerRunning(true);

    logSetMutation.mutate(
      {
        workout_exercise_id: exercise.id,
        set_number: set.setNumber,
        reps_completed: set.reps ? Number(set.reps) : null,
        weight_kg: set.weight ? Number(set.weight) : null,
        duration_seconds: null,
        is_warmup: false,
        scheduled_workout_id: entryId,
        planId,
      },
      {
        onSuccess: () => {
          setSetEntries((prev) => {
            const next = [...prev];
            next[setIndex] = { ...next[setIndex], completed: true };
            return next;
          });
          const isLastSet = setEntries.filter((s) => !s.completed).length <= 1;
          if (!isLastSet && exercise.target_rest_seconds) {
            setRestTimer(exercise.target_rest_seconds);
          }
        },
        onError: () => toast.error('Не удалось сохранить подход'),
      }
    );
  };

  const handleFinishWorkout = () => {
    toggleCompleteMutation.mutate(entryId, {
      onSuccess: () => {
        toast.success('Тренировка завершена!');
        router.push('/workouts');
      },
    });
  };

  const goToNextExercise = () => {
    if (!session) return;
    if (currentExerciseIndex < session.exercises.length - 1) {
      setCurrentExerciseIndex((p) => p + 1);
      setRestTimer(0);
    }
  };

  const goToPrevExercise = () => {
    if (currentExerciseIndex > 0) {
      setCurrentExerciseIndex((p) => p - 1);
      setRestTimer(0);
    }
  };

  if (planLoading || !plan) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-12">
        <Dumbbell className="size-12 text-muted-foreground" />
        <p className="text-lg font-semibold">Сессия не найдена</p>
        <Button asChild>
          <Link href="/workouts">Назад к тренировкам</Link>
        </Button>
      </div>
    );
  }

  const exercise = session.exercises[currentExerciseIndex];
  const allSetsCompleted = setEntries.length > 0 && setEntries.every((s) => s.completed);
  const isLastExercise = currentExerciseIndex === session.exercises.length - 1;
  const totalExercises = session.exercises.length;

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/workouts">
            <ArrowLeft className="size-5" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-xl font-bold tracking-tight sm:text-2xl">
            День {session.day_number}: {session.name}
          </h1>
        </div>
      </div>

      {/* Timer + progress */}
      <Card className="border-border/50">
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div
                className={`flex size-10 items-center justify-center rounded-full ${
                  isTimerRunning ? 'bg-green-500/10' : 'bg-muted'
                }`}
              >
                <Clock className={`size-5 ${isTimerRunning ? 'text-green-500' : 'text-muted-foreground'}`} />
              </div>
              <div>
                <p className="text-2xl font-bold tabular-nums">{formatTime(elapsedTime)}</p>
                <p className="text-xs text-muted-foreground">Время тренировки</p>
              </div>
              <Button variant="outline" size="icon" onClick={() => setIsTimerRunning(!isTimerRunning)}>
                {isTimerRunning ? <Pause className="size-4" /> : <Play className="size-4" />}
              </Button>
            </div>
            <div className="text-sm text-muted-foreground">
              Упражнение {currentExerciseIndex + 1} из {totalExercises}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Rest timer */}
      {restTimer > 0 && (
        <Card className="border-blue-500/30 bg-blue-500/5">
          <CardContent className="flex items-center gap-4 pt-6">
            <Timer className="size-6 text-blue-500" />
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Отдых</p>
              <Progress
                value={
                  exercise?.target_rest_seconds
                    ? ((exercise.target_rest_seconds - restTimer) / exercise.target_rest_seconds) * 100
                    : 0
                }
                className="mt-1 h-2"
              />
            </div>
            <span className="text-2xl font-bold tabular-nums text-blue-600 dark:text-blue-400">
              {formatTime(restTimer)}
            </span>
            <Button variant="outline" size="sm" onClick={() => setRestTimer(0)}>
              Пропустить
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Current exercise */}
      {exercise && (
        <Card className="border-border/50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-full bg-primary/10 text-lg font-bold text-primary">
                {currentExerciseIndex + 1}
              </div>
              <div>
                <CardTitle className="text-lg">
                  {exercise.exercise_name_ru ?? exercise.exercise_name ?? 'Упражнение'}
                </CardTitle>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  {exercise.target_sets}&times;{exercise.target_reps}
                  {exercise.target_rest_seconds ? ` | отдых ${exercise.target_rest_seconds}с` : ''}
                </p>
              </div>
              {allSetsCompleted && <CheckCircle2 className="ml-auto size-6 text-green-500" />}
            </div>
            {exercise.notes && (
              <p className="mt-3 rounded-md bg-muted/50 px-3 py-2 text-sm text-muted-foreground">
                {exercise.notes}
              </p>
            )}
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-left text-xs text-muted-foreground">
                    <th className="pb-2 pr-3 font-medium">Подход</th>
                    <th className="pb-2 pr-3 font-medium">Вес (кг)</th>
                    <th className="pb-2 pr-3 font-medium">Повторения</th>
                    <th className="pb-2 font-medium"></th>
                  </tr>
                </thead>
                <tbody>
                  {setEntries.map((set, setIndex) => (
                    <tr key={setIndex} className="border-b border-border/30 last:border-0">
                      <td className="py-3 pr-3">
                        <Badge
                          variant={set.completed ? 'default' : 'secondary'}
                          className="min-w-8 justify-center"
                        >
                          {set.setNumber}
                        </Badge>
                      </td>
                      <td className="py-3 pr-3">
                        <Input
                          type="number"
                          placeholder="0"
                          value={set.weight}
                          onChange={(e) => updateSet(setIndex, 'weight', e.target.value)}
                          disabled={set.completed}
                          className="h-9 w-24"
                        />
                      </td>
                      <td className="py-3 pr-3">
                        <Input
                          type="number"
                          placeholder="0"
                          value={set.reps}
                          onChange={(e) => updateSet(setIndex, 'reps', e.target.value)}
                          disabled={set.completed}
                          className="h-9 w-24"
                        />
                      </td>
                      <td className="py-3">
                        {!set.completed ? (
                          <Button
                            size="sm"
                            onClick={() => completeSet(setIndex)}
                            disabled={!set.reps || !set.weight || logSetMutation.isPending}
                          >
                            {logSetMutation.isPending ? (
                              <Loader2 className="size-4 animate-spin" />
                            ) : (
                              <CheckCircle2 className="size-4" />
                            )}
                            Готово
                          </Button>
                        ) : (
                          <CheckCircle2 className="size-5 text-green-500" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button variant="outline" onClick={goToPrevExercise} disabled={currentExerciseIndex === 0}>
          <ArrowLeft className="size-4" />
          Предыдущее
        </Button>

        {allSetsCompleted && !isLastExercise ? (
          <Button onClick={goToNextExercise}>
            Следующее упражнение
            <ArrowRight className="size-4" />
          </Button>
        ) : isLastExercise && allSetsCompleted ? (
          <Button onClick={handleFinishWorkout} disabled={toggleCompleteMutation.isPending}>
            {toggleCompleteMutation.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Dumbbell className="size-4" />
            )}
            Завершить тренировку
          </Button>
        ) : (
          <Button variant="outline" onClick={goToNextExercise} disabled={isLastExercise}>
            Пропустить
            <ArrowRight className="size-4" />
          </Button>
        )}
      </div>

      {/* Exercise list mini-nav */}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {session.exercises.map((ex, idx) => (
          <button
            key={ex.id}
            type="button"
            onClick={() => { setCurrentExerciseIndex(idx); setRestTimer(0); }}
            className={`flex size-8 shrink-0 items-center justify-center rounded-full text-xs font-medium transition-colors ${
              idx === currentExerciseIndex
                ? 'bg-primary text-primary-foreground'
                : idx < currentExerciseIndex
                  ? 'bg-green-500/10 text-green-600 dark:text-green-400'
                  : 'bg-muted text-muted-foreground'
            }`}
          >
            {idx + 1}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── Entry Resolver ──────────────────────────────────────────────────────────
// Ensures we always have a ScheduledWorkout entry before starting the session.

function WorkoutSessionResolver({
  planId,
  sessionId,
  entryId,
}: {
  planId: string;
  sessionId: string;
  entryId: string | null;
}) {
  const router = useRouter();
  const startWorkoutMutation = useStartWorkout();
  const [resolvedEntryId, setResolvedEntryId] = useState<string | null>(entryId);

  useEffect(() => {
    if (resolvedEntryId) return;

    // No entry ID provided — create/find one for today
    const today = new Date().toISOString().split('T')[0];
    startWorkoutMutation.mutate(
      { session_id: sessionId, scheduled_date: today },
      {
        onSuccess: (entry) => {
          setResolvedEntryId(entry.id);
          // Update URL with entry param without full navigation
          router.replace(`/workouts/${planId}?session=${sessionId}&entry=${entry.id}`);
        },
        onError: () => {
          toast.error('Не удалось начать тренировку');
          router.push('/workouts');
        },
      }
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!resolvedEntryId) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-12">
        <Loader2 className="size-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Подготовка тренировки...</p>
      </div>
    );
  }

  return (
    <WorkoutSessionView
      planId={planId}
      sessionId={sessionId}
      entryId={resolvedEntryId}
    />
  );
}

// ─── Page Router ─────────────────────────────────────────────────────────────

export default function WorkoutDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const workoutId = params.workoutId as string;
  const sessionId = searchParams.get('session');
  const entryId = searchParams.get('entry');

  if (sessionId) {
    return (
      <WorkoutSessionResolver
        planId={workoutId}
        sessionId={sessionId}
        entryId={entryId}
      />
    );
  }

  return <PlanOverview planId={workoutId} />;
}
