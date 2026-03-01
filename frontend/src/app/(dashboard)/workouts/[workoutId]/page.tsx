'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  Clock,
  Plus,
  CheckCircle2,
  Timer,
  Dumbbell,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import type { WorkoutSession, ExerciseSet } from '@/types/workout';

// --- Mock data ---
const mockSession: WorkoutSession = {
  id: 's1',
  day_number: 1,
  name: 'Push Day (Грудь, Плечи, Трицепс)',
  notes: 'Разминка 5-10 минут на кардио перед тренировкой',
  order_index: 0,
  exercises: [
    {
      id: 'e1',
      exercise_id: 'ex1',
      exercise_name: 'Bench Press',
      exercise_name_ru: 'Жим штанги лёжа',
      order_index: 0,
      target_sets: 4,
      target_reps: '8-10',
      target_rest_seconds: 120,
      notes: 'Контролируйте негативную фазу',
      logged_sets: [
        { id: 'ls1', set_number: 1, reps_completed: 10, weight_kg: 80, duration_seconds: null, is_warmup: false, completed_at: '2025-01-15T10:05:00Z' },
        { id: 'ls2', set_number: 2, reps_completed: 9, weight_kg: 80, duration_seconds: null, is_warmup: false, completed_at: '2025-01-15T10:08:00Z' },
      ],
    },
    {
      id: 'e2',
      exercise_id: 'ex2',
      exercise_name: 'Overhead Press',
      exercise_name_ru: 'Жим штанги стоя',
      order_index: 1,
      target_sets: 3,
      target_reps: '10-12',
      target_rest_seconds: 90,
      notes: null,
      logged_sets: [],
    },
    {
      id: 'e3',
      exercise_id: 'ex3',
      exercise_name: 'Incline Dumbbell Press',
      exercise_name_ru: 'Жим гантелей на наклонной скамье',
      order_index: 2,
      target_sets: 3,
      target_reps: '10-12',
      target_rest_seconds: 90,
      notes: null,
      logged_sets: [],
    },
    {
      id: 'e4',
      exercise_id: 'ex4',
      exercise_name: 'Lateral Raises',
      exercise_name_ru: 'Разводка гантелей в стороны',
      order_index: 3,
      target_sets: 3,
      target_reps: '12-15',
      target_rest_seconds: 60,
      notes: null,
      logged_sets: [],
    },
    {
      id: 'e5',
      exercise_id: 'ex5',
      exercise_name: 'Triceps Pushdown',
      exercise_name_ru: 'Разгибание рук на блоке',
      order_index: 4,
      target_sets: 3,
      target_reps: '12-15',
      target_rest_seconds: 60,
      notes: null,
      logged_sets: [],
    },
  ],
};

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

export default function WorkoutSessionPage() {
  const params = useParams();
  const _workoutId = params.workoutId;

  const [elapsedTime, setElapsedTime] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(true);
  const [restTimers, setRestTimers] = useState<Record<string, number>>({});
  const [expandedExercises, setExpandedExercises] = useState<Record<string, boolean>>({
    e1: true,
    e2: true,
  });

  const [setEntries, setSetEntries] = useState<Record<string, SetEntry[]>>(() => {
    const entries: Record<string, SetEntry[]> = {};
    mockSession.exercises.forEach((exercise) => {
      const sets: SetEntry[] = [];
      // Pre-fill from logged sets
      exercise.logged_sets.forEach((ls) => {
        sets.push({
          setNumber: ls.set_number,
          reps: ls.reps_completed?.toString() ?? '',
          weight: ls.weight_kg?.toString() ?? '',
          completed: true,
        });
      });
      // Fill remaining target sets
      for (let i = sets.length; i < exercise.target_sets; i++) {
        sets.push({
          setNumber: i + 1,
          reps: '',
          weight: '',
          completed: false,
        });
      }
      entries[exercise.id] = sets;
    });
    return entries;
  });

  // Workout timer
  useEffect(() => {
    if (!isTimerRunning) return;
    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  // Rest timers
  useEffect(() => {
    const interval = setInterval(() => {
      setRestTimers((prev) => {
        const next = { ...prev };
        let changed = false;
        for (const key of Object.keys(next)) {
          if (next[key] > 0) {
            next[key] = next[key] - 1;
            changed = true;
          }
        }
        return changed ? next : prev;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const toggleExercise = (id: string) => {
    setExpandedExercises((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const updateSet = (exerciseId: string, setIndex: number, field: 'reps' | 'weight', value: string) => {
    setSetEntries((prev) => {
      const sets = [...prev[exerciseId]];
      sets[setIndex] = { ...sets[setIndex], [field]: value };
      return { ...prev, [exerciseId]: sets };
    });
  };

  const completeSet = useCallback((exerciseId: string, setIndex: number, restSeconds: number | null) => {
    setSetEntries((prev) => {
      const sets = [...prev[exerciseId]];
      sets[setIndex] = { ...sets[setIndex], completed: true };
      return { ...prev, [exerciseId]: sets };
    });
    if (restSeconds) {
      setRestTimers((prev) => ({ ...prev, [exerciseId]: restSeconds }));
    }
  }, []);

  const addSet = (exerciseId: string) => {
    setSetEntries((prev) => {
      const sets = [...prev[exerciseId]];
      sets.push({
        setNumber: sets.length + 1,
        reps: '',
        weight: '',
        completed: false,
      });
      return { ...prev, [exerciseId]: sets };
    });
  };

  const totalSets = mockSession.exercises.reduce((acc, ex) => acc + ex.target_sets, 0);
  const completedSets = Object.values(setEntries).reduce(
    (acc, sets) => acc + sets.filter((s) => s.completed).length,
    0
  );
  const progressPercent = totalSets > 0 ? Math.round((completedSets / totalSets) * 100) : 0;

  return (
    <div className="flex flex-col gap-6">
      {/* Back and header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/workouts">
            <ArrowLeft className="size-5" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-xl font-bold tracking-tight sm:text-2xl">
            День {mockSession.day_number}: {mockSession.name}
          </h1>
          {mockSession.notes && (
            <p className="mt-1 text-sm text-muted-foreground">{mockSession.notes}</p>
          )}
        </div>
      </div>

      {/* Timer and progress bar */}
      <Card className="border-border/50">
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div
                  className={`flex size-10 items-center justify-center rounded-full ${
                    isTimerRunning ? 'bg-green-500/10' : 'bg-muted'
                  }`}
                >
                  <Clock
                    className={`size-5 ${
                      isTimerRunning ? 'text-green-500' : 'text-muted-foreground'
                    }`}
                  />
                </div>
                <div>
                  <p className="text-2xl font-bold tabular-nums">{formatTime(elapsedTime)}</p>
                  <p className="text-xs text-muted-foreground">Время тренировки</p>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsTimerRunning(!isTimerRunning)}
              >
                {isTimerRunning ? 'Пауза' : 'Продолжить'}
              </Button>
            </div>
            <div className="flex flex-col gap-1 sm:items-end">
              <p className="text-sm text-muted-foreground">
                Выполнено: {completedSets} / {totalSets} подходов
              </p>
              <Progress value={progressPercent} className="h-2 w-full sm:w-48" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Exercise list */}
      <div className="flex flex-col gap-4">
        {mockSession.exercises.map((exercise, exerciseIndex) => {
          const isExpanded = expandedExercises[exercise.id] ?? false;
          const exerciseSets = setEntries[exercise.id] ?? [];
          const exerciseCompleted = exerciseSets.every((s) => s.completed);
          const restTime = restTimers[exercise.id] ?? 0;

          return (
            <Card
              key={exercise.id}
              className={`border-border/50 transition-all ${
                exerciseCompleted ? 'border-green-500/30 bg-green-500/5' : ''
              }`}
            >
              <CardHeader
                className="cursor-pointer"
                onClick={() => toggleExercise(exercise.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex size-8 items-center justify-center rounded-full bg-muted text-sm font-medium">
                      {exerciseIndex + 1}
                    </div>
                    <div>
                      <CardTitle className="text-base">
                        {exercise.exercise_name_ru ?? exercise.exercise_name}
                      </CardTitle>
                      <p className="mt-0.5 text-sm text-muted-foreground">
                        {exercise.target_sets}&times;{exercise.target_reps}
                        {exercise.target_rest_seconds
                          ? ` | отдых ${exercise.target_rest_seconds}с`
                          : ''}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {exerciseCompleted && (
                      <CheckCircle2 className="size-5 text-green-500" />
                    )}
                    {isExpanded ? (
                      <ChevronUp className="size-4 text-muted-foreground" />
                    ) : (
                      <ChevronDown className="size-4 text-muted-foreground" />
                    )}
                  </div>
                </div>
              </CardHeader>

              {isExpanded && (
                <CardContent>
                  {exercise.notes && (
                    <p className="mb-4 rounded-md bg-muted/50 px-3 py-2 text-sm text-muted-foreground">
                      {exercise.notes}
                    </p>
                  )}

                  {/* Rest timer */}
                  {restTime > 0 && (
                    <div className="mb-4 flex items-center gap-3 rounded-lg border border-blue-500/30 bg-blue-500/5 p-3">
                      <Timer className="size-5 text-blue-500" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-blue-600 dark:text-blue-400">
                          Отдых
                        </p>
                        <Progress
                          value={
                            exercise.target_rest_seconds
                              ? ((exercise.target_rest_seconds - restTime) /
                                  exercise.target_rest_seconds) *
                                100
                              : 0
                          }
                          className="mt-1 h-1.5"
                        />
                      </div>
                      <span className="text-lg font-bold tabular-nums text-blue-600 dark:text-blue-400">
                        {formatTime(restTime)}
                      </span>
                    </div>
                  )}

                  {/* Sets table */}
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
                        {exerciseSets.map((set, setIndex) => (
                          <tr key={setIndex} className="border-b border-border/30 last:border-0">
                            <td className="py-2.5 pr-3">
                              <Badge
                                variant={set.completed ? 'default' : 'secondary'}
                                className="min-w-8 justify-center"
                              >
                                {set.setNumber}
                              </Badge>
                            </td>
                            <td className="py-2.5 pr-3">
                              <Input
                                type="number"
                                placeholder="0"
                                value={set.weight}
                                onChange={(e) =>
                                  updateSet(exercise.id, setIndex, 'weight', e.target.value)
                                }
                                disabled={set.completed}
                                className="h-8 w-20"
                              />
                            </td>
                            <td className="py-2.5 pr-3">
                              <Input
                                type="number"
                                placeholder="0"
                                value={set.reps}
                                onChange={(e) =>
                                  updateSet(exercise.id, setIndex, 'reps', e.target.value)
                                }
                                disabled={set.completed}
                                className="h-8 w-20"
                              />
                            </td>
                            <td className="py-2.5">
                              {!set.completed ? (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() =>
                                    completeSet(
                                      exercise.id,
                                      setIndex,
                                      exercise.target_rest_seconds
                                    )
                                  }
                                  disabled={!set.reps || !set.weight}
                                  className="h-8"
                                >
                                  <CheckCircle2 className="size-3.5" />
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

                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-3 w-full"
                    onClick={() => addSet(exercise.id)}
                  >
                    <Plus className="size-3.5" />
                    Добавить подход
                  </Button>
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>

      {/* Finish workout */}
      <Separator />
      <div className="flex justify-center pb-4">
        <Button size="lg" className="w-full sm:w-auto" asChild>
          <Link href="/workouts">
            <Dumbbell className="size-4" />
            Завершить тренировку
          </Link>
        </Button>
      </div>
    </div>
  );
}
