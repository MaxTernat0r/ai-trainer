'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import {
  Dumbbell,
  Plus,
  Calendar,
  Clock,
  ChevronRight,
  ChevronLeft,
  Sparkles,
  CheckCircle2,
  Zap,
  Trash2,
  X,
  Loader2,
  CalendarDays,
  GripVertical,
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Skeleton } from '@/components/ui/skeleton';
import {
  useWorkoutPlans,
  useWorkoutPlan,
  useGenerateWorkout,
  useDeleteWorkoutPlan,
  useActivateWorkoutPlan,
  useWorkoutCalendar,
  useRescheduleEntry,
  useAutoSchedulePlan,
  useToggleComplete,
  useAddScheduleEntry,
  useDeleteScheduleEntry,
} from '@/lib/queries/use-workouts';

const difficultyLabels: Record<string, string> = {
  beginner: 'Начинающий',
  intermediate: 'Средний',
  advanced: 'Продвинутый',
};

const difficultyColors: Record<string, string> = {
  beginner: 'bg-green-500/10 text-green-600 dark:text-green-400',
  intermediate: 'bg-yellow-500/10 text-yellow-600 dark:text-yellow-400',
  advanced: 'bg-red-500/10 text-red-600 dark:text-red-400',
};

const goalLabels: Record<string, string> = {
  muscle_gain: 'Набор массы',
  fat_loss: 'Жиросжигание',
  strength: 'Сила',
  endurance: 'Выносливость',
};

const WEEKDAY_NAMES = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
const MONTH_NAMES = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
];

export default function WorkoutsPage() {
  const [sheetOpen, setSheetOpen] = useState(false);
  const [weeks, setWeeks] = useState([8]);
  const [daysPerWeek, setDaysPerWeek] = useState('4');
  const [periodization, setPeriodization] = useState('linear');
  const [rescheduleEntryId, setRescheduleEntryId] = useState<string | null>(null);
  const [addingForDate, setAddingForDate] = useState<string | null>(null);

  // Calendar state
  const now = new Date();
  const [calendarYear, setCalendarYear] = useState(now.getFullYear());
  const [calendarMonth, setCalendarMonth] = useState(now.getMonth() + 1);

  // Query hooks
  const { data: plans, isLoading: plansLoading } = useWorkoutPlans();
  const generateMutation = useGenerateWorkout();
  const deleteMutation = useDeleteWorkoutPlan();
  const activateMutation = useActivateWorkoutPlan();
  const rescheduleMutation = useRescheduleEntry();
  const autoScheduleMutation = useAutoSchedulePlan();
  const toggleCompleteMutation = useToggleComplete();
  const addEntryMutation = useAddScheduleEntry();
  const deleteEntryMutation = useDeleteScheduleEntry();

  const activePlan = plans?.find((p) => p.is_active) ?? null;
  const inactivePlans = plans?.filter((p) => !p.is_active) ?? [];

  // Fetch full active plan to show sessions
  const { data: activePlanFull } = useWorkoutPlan(activePlan?.id);

  // Calendar data
  const { data: calendarEntries } = useWorkoutCalendar(calendarYear, calendarMonth);

  // Build calendar grid
  const calendarDays = useMemo(() => {
    const firstDay = new Date(calendarYear, calendarMonth - 1, 1);
    const lastDay = new Date(calendarYear, calendarMonth, 0);
    const daysInMonth = lastDay.getDate();

    // Monday = 0, Sunday = 6
    let startOffset = firstDay.getDay() - 1;
    if (startOffset < 0) startOffset = 6;

    const days: { date: number; entries: typeof calendarEntries }[] = [];

    // Empty slots before first day
    for (let i = 0; i < startOffset; i++) {
      days.push({ date: 0, entries: [] });
    }

    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${calendarYear}-${String(calendarMonth).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      const dayEntries = calendarEntries?.filter((e) => e.scheduled_date === dateStr) ?? [];
      days.push({ date: d, entries: dayEntries });
    }

    return days;
  }, [calendarYear, calendarMonth, calendarEntries]);

  const handlePrevMonth = () => {
    if (calendarMonth === 1) {
      setCalendarMonth(12);
      setCalendarYear(calendarYear - 1);
    } else {
      setCalendarMonth(calendarMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (calendarMonth === 12) {
      setCalendarMonth(1);
      setCalendarYear(calendarYear + 1);
    } else {
      setCalendarMonth(calendarMonth + 1);
    }
  };

  const handleReschedule = (entryId: string, newDate: string) => {
    rescheduleMutation.mutate(
      { entryId, scheduledDate: newDate },
      {
        onSuccess: () => {
          toast.success('Тренировка перенесена');
          setRescheduleEntryId(null);
        },
        onError: () => {
          toast.error('Не удалось перенести тренировку');
        },
      }
    );
  };

  const handleAutoSchedule = (planId: string) => {
    autoScheduleMutation.mutate(planId, {
      onSuccess: () => {
        toast.success('Тренировки распределены по календарю');
      },
      onError: () => {
        toast.error('Не удалось составить расписание');
      },
    });
  };

  const handleGenerate = () => {
    generateMutation.mutate(
      {
        weeks: weeks[0],
        days_per_week: Number(daysPerWeek),
        periodization,
      },
      {
        onSuccess: () => {
          setSheetOpen(false);
          toast.success('Программа успешно сгенерирована!');
        },
        onError: (error) => {
          toast.error(
            `Ошибка генерации: ${error.message || 'попробуйте ещё раз'}`
          );
        },
      }
    );
  };

  const handleDelete = (planId: string) => {
    deleteMutation.mutate(planId, {
      onSuccess: () => {
        toast.success('Программа удалена');
      },
      onError: () => {
        toast.error('Не удалось удалить программу');
      },
    });
  };

  const handleActivate = (planId: string) => {
    activateMutation.mutate(planId, {
      onSuccess: () => {
        toast.success('Программа активирована');
      },
      onError: () => {
        toast.error('Не удалось активировать программу');
      },
    });
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Тренировки</h1>
          <p className="text-muted-foreground">
            Управляйте программами тренировок и отслеживайте прогресс
          </p>
        </div>
        <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
          <SheetTrigger asChild>
            <Button>
              <Plus className="size-4" />
              Создать новую программу
            </Button>
          </SheetTrigger>
          <SheetContent>
            <SheetHeader>
              <SheetTitle>Создать программу тренировок</SheetTitle>
              <SheetDescription>
                ИИ-тренер составит персональную программу на основе ваших параметров
              </SheetDescription>
            </SheetHeader>
            <div className="flex flex-col gap-6 p-4">
              {/* Weeks selector */}
              <div className="flex flex-col gap-3">
                <Label>Длительность (недели): {weeks[0]}</Label>
                <Slider
                  value={weeks}
                  onValueChange={setWeeks}
                  min={1}
                  max={12}
                  step={1}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>1 нед.</span>
                  <span>12 нед.</span>
                </div>
              </div>

              {/* Days per week */}
              <div className="flex flex-col gap-3">
                <Label>Дней в неделю</Label>
                <Select value={daysPerWeek} onValueChange={setDaysPerWeek}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="2">2 дня</SelectItem>
                    <SelectItem value="3">3 дня</SelectItem>
                    <SelectItem value="4">4 дня</SelectItem>
                    <SelectItem value="5">5 дней</SelectItem>
                    <SelectItem value="6">6 дней</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Periodization */}
              <div className="flex flex-col gap-3">
                <Label>Периодизация</Label>
                <Select value={periodization} onValueChange={setPeriodization}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="linear">Линейная</SelectItem>
                    <SelectItem value="undulating">Волнообразная</SelectItem>
                    <SelectItem value="block">Блочная</SelectItem>
                    <SelectItem value="none">Без периодизации</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Separator />

              <div className="rounded-lg border border-dashed border-border p-4">
                <div className="flex items-start gap-3">
                  <Sparkles className="mt-0.5 size-5 text-primary" />
                  <div className="flex flex-col gap-1">
                    <p className="text-sm font-medium">ИИ подберёт программу</p>
                    <p className="text-xs text-muted-foreground">
                      На основе ваших целей, уровня подготовки и доступного оборудования
                    </p>
                  </div>
                </div>
              </div>

              <Button
                className="w-full"
                onClick={handleGenerate}
                disabled={generateMutation.isPending}
              >
                {generateMutation.isPending ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    Генерация... Это может занять до 30 секунд
                  </>
                ) : (
                  <>
                    <Sparkles className="size-4" />
                    Сгенерировать программу
                  </>
                )}
              </Button>
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* Loading state */}
      {plansLoading && (
        <div className="flex flex-col gap-4">
          <Card className="border-border/50">
            <CardHeader>
              <div className="flex items-center gap-3">
                <Skeleton className="size-10 rounded-lg" />
                <div className="flex-1">
                  <Skeleton className="mb-2 h-5 w-1/3" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex gap-6">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-24" />
              </div>
            </CardContent>
          </Card>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="border-border/50">
                <CardHeader className="pb-2">
                  <Skeleton className="mb-2 h-5 w-16 rounded-full" />
                  <Skeleton className="h-5 w-3/4" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-4 w-1/2" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* No plans CTA */}
      {!plansLoading && plans && plans.length === 0 && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center gap-4 py-12">
            <div className="flex size-16 items-center justify-center rounded-full bg-primary/10">
              <Dumbbell className="size-8 text-primary" />
            </div>
            <div className="text-center">
              <h3 className="text-lg font-semibold">
                У вас ещё нет программы тренировок
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Создайте персональную программу с помощью ИИ-тренера или выберите из готовых
              </p>
            </div>
            <Button onClick={() => setSheetOpen(true)}>
              <Plus className="size-4" />
              Создать программу
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Active plan */}
      {!plansLoading && activePlan && (
        <>
          {/* Plan info card */}
          <Card className="border-border/50">
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10">
                    <Zap className="size-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{activePlan.title}</CardTitle>
                    <CardDescription>
                      {goalLabels[activePlan.goal] ?? activePlan.goal}
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {activePlan.is_ai_generated && (
                    <Badge variant="secondary" className="gap-1">
                      <Sparkles className="size-3" />
                      ИИ
                    </Badge>
                  )}
                  <Badge
                    variant="outline"
                    className={difficultyColors[activePlan.difficulty] ?? ''}
                  >
                    {difficultyLabels[activePlan.difficulty] ?? activePlan.difficulty}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-6">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="size-4" />
                  <span>{activePlan.duration_weeks} недель</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="size-4" />
                  <span>{activePlan.days_per_week} дня в неделю</span>
                </div>
                {activePlanFull && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Dumbbell className="size-4" />
                    <span>{activePlanFull.sessions.length} тренировок</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Sessions grid */}
          {activePlanFull && activePlanFull.sessions.length > 0 && (
            <div>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">Тренировочные дни</h2>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleAutoSchedule(activePlanFull.id)}
                  disabled={autoScheduleMutation.isPending}
                >
                  {autoScheduleMutation.isPending ? (
                    <Loader2 className="size-4 animate-spin" />
                  ) : (
                    <CalendarDays className="size-4" />
                  )}
                  Распределить по календарю
                </Button>
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {activePlanFull.sessions.map((session) => (
                  <Link key={session.id} href={`/workouts/${activePlanFull.id}?session=${session.id}`}>
                    <Card className="h-full cursor-pointer border-border/50 transition-colors hover:border-primary/30 hover:shadow-md">
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between">
                          <Badge variant="secondary" className="mb-2">
                            День {session.day_number}
                          </Badge>
                          <ChevronRight className="size-4 text-muted-foreground" />
                        </div>
                        <CardTitle className="text-base">{session.name}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Dumbbell className="size-4" />
                          <span>
                            {session.exercises.length}{' '}
                            {session.exercises.length === 1
                              ? 'упражнение'
                              : session.exercises.length < 5
                                ? 'упражнения'
                                : 'упражнений'}
                          </span>
                        </div>
                        {session.scheduled_date && (
                          <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                            <Calendar className="size-3" />
                            <span>
                              {new Date(session.scheduled_date).toLocaleDateString('ru-RU', {
                                day: 'numeric',
                                month: 'short',
                              })}
                            </span>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Calendar */}
          <Card className="border-border/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <CalendarDays className="size-5" />
                  Календарь тренировок
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="icon" onClick={handlePrevMonth}>
                    <ChevronLeft className="size-4" />
                  </Button>
                  <span className="min-w-[140px] text-center text-sm font-medium">
                    {MONTH_NAMES[calendarMonth - 1]} {calendarYear}
                  </span>
                  <Button variant="ghost" size="icon" onClick={handleNextMonth}>
                    <ChevronRight className="size-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Weekday headers */}
              <div className="grid grid-cols-7 gap-1">
                {WEEKDAY_NAMES.map((day) => (
                  <div key={day} className="p-2 text-center text-xs font-medium text-muted-foreground">
                    {day}
                  </div>
                ))}
                {/* Calendar days */}
                {calendarDays.map((cell, idx) => {
                  const isToday =
                    cell.date > 0 &&
                    calendarYear === now.getFullYear() &&
                    calendarMonth === now.getMonth() + 1 &&
                    cell.date === now.getDate();

                  return (
                    <div
                      key={idx}
                      className={`relative min-h-[72px] rounded-md border p-1 text-xs ${
                        cell.date === 0
                          ? 'border-transparent'
                          : isToday
                            ? 'border-primary/50 bg-primary/5'
                            : 'border-border/30'
                      }`}
                      onClick={() => {
                        if (cell.date === 0) return;
                        const dateStr = `${calendarYear}-${String(calendarMonth).padStart(2, '0')}-${String(cell.date).padStart(2, '0')}`;

                        if (rescheduleEntryId) {
                          handleReschedule(rescheduleEntryId, dateStr);
                          return;
                        }

                        // Click empty area of a day → toggle add-session picker
                        setAddingForDate(addingForDate === dateStr ? null : dateStr);
                      }}
                    >
                      {cell.date > 0 && (
                        <>
                          <span className={`text-xs ${isToday ? 'font-bold text-primary' : 'text-muted-foreground'}`}>
                            {cell.date}
                          </span>
                          <div className="mt-0.5 flex flex-col gap-0.5">
                            {cell.entries?.map((entry) => (
                              <div
                                key={entry.id}
                                className={`group/entry flex items-center gap-1 rounded px-1 py-0.5 text-[10px] leading-tight ${
                                  entry.is_completed
                                    ? 'bg-green-500/10 text-green-600 dark:text-green-400'
                                    : 'bg-primary/10 text-primary'
                                }`}
                              >
                                <button
                                  className="shrink-0 rounded p-0.5 transition-colors hover:bg-muted/50"
                                  title={entry.is_completed ? 'Отметить как невыполненную' : 'Отметить как выполненную'}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleCompleteMutation.mutate(entry.id);
                                  }}
                                >
                                  <CheckCircle2 className={`size-3 ${entry.is_completed ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground/40'}`} />
                                </button>
                                <Link
                                  href={`/workouts/${entry.plan_id}?session=${entry.session_id}&entry=${entry.id}`}
                                  className="truncate hover:underline"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  {entry.session_name}
                                </Link>
                                <div className="ml-auto flex shrink-0 items-center gap-0.5 opacity-0 transition-opacity group-hover/entry:opacity-100">
                                  {!entry.is_completed && (
                                    <button
                                      className="rounded p-0.5 hover:bg-muted"
                                      title="Перенести"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        setRescheduleEntryId(
                                          rescheduleEntryId === entry.id
                                            ? null
                                            : entry.id
                                        );
                                      }}
                                    >
                                      <GripVertical className="size-3" />
                                    </button>
                                  )}
                                  <button
                                    className="rounded p-0.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                                    title="Удалить из календаря"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      deleteEntryMutation.mutate(entry.id);
                                    }}
                                  >
                                    <X className="size-3" />
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </>
                      )}
                      {rescheduleEntryId && cell.date > 0 && (
                        <div className="absolute inset-0 cursor-pointer rounded-md bg-primary/5 opacity-0 transition-opacity hover:opacity-100" />
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Session picker when clicking an empty day */}
              {addingForDate && activePlanFull && (
                <div className="mt-3 rounded-lg border border-primary/30 bg-primary/5 px-3 py-2">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm">
                      Добавить тренировку на{' '}
                      {new Date(addingForDate + 'T00:00:00').toLocaleDateString('ru-RU', {
                        day: 'numeric',
                        month: 'long',
                      })}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setAddingForDate(null)}
                    >
                      Отмена
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {activePlanFull.sessions.map((session) => (
                      <Button
                        key={session.id}
                        variant="outline"
                        size="sm"
                        disabled={addEntryMutation.isPending}
                        onClick={() => {
                          addEntryMutation.mutate(
                            {
                              session_id: session.id,
                              scheduled_date: addingForDate,
                              is_completed: false,
                            },
                            {
                              onSuccess: () => {
                                toast.success('Тренировка добавлена');
                                setAddingForDate(null);
                              },
                              onError: () => {
                                toast.error('Не удалось добавить тренировку');
                              },
                            }
                          );
                        }}
                      >
                        {session.name}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {rescheduleEntryId && (
                <div className="mt-3 flex items-center justify-between rounded-lg border border-primary/30 bg-primary/5 px-3 py-2 text-sm">
                  <span>Выберите новую дату для тренировки</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setRescheduleEntryId(null)}
                  >
                    Отмена
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* All plans */}
      {!plansLoading && plans && plans.length > 0 && (
        <>
          <Separator />
          <div>
            <h2 className="mb-4 text-lg font-semibold">Все программы</h2>
            <div className="flex flex-col gap-3">
              {plans.map((plan) => (
                <Link key={plan.id} href={`/workouts/${plan.id}`} className="block">
                  <Card
                    className={`cursor-pointer border-border/50 transition-colors hover:border-primary/30 ${
                      plan.is_active ? 'ring-2 ring-primary/20' : ''
                    }`}
                  >
                    <CardContent className="flex items-center justify-between pt-6">
                      <div className="flex min-w-0 flex-1 items-center gap-4">
                        <div
                          className={`flex size-10 shrink-0 items-center justify-center rounded-lg ${
                            plan.is_active ? 'bg-primary/10' : 'bg-muted'
                          }`}
                        >
                          <Dumbbell
                            className={`size-5 ${
                              plan.is_active ? 'text-primary' : 'text-muted-foreground'
                            }`}
                          />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{plan.title}</p>
                            {plan.is_active && (
                              <Badge variant="default" className="gap-1 text-xs">
                                <CheckCircle2 className="size-3" />
                                Активная
                              </Badge>
                            )}
                          </div>
                          <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                            <span>{goalLabels[plan.goal] ?? plan.goal}</span>
                            <span>{plan.duration_weeks} нед.</span>
                            <span>{plan.days_per_week} дн/нед.</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex shrink-0 items-center gap-2" onClick={(e) => e.preventDefault()}>
                        <Badge
                          variant="outline"
                          className={difficultyColors[plan.difficulty] ?? ''}
                        >
                          {difficultyLabels[plan.difficulty] ?? plan.difficulty}
                        </Badge>
                        {!plan.is_active && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={(e) => { e.stopPropagation(); handleActivate(plan.id); }}
                              disabled={activateMutation.isPending}
                            >
                              {activateMutation.isPending ? (
                                <Loader2 className="size-3 animate-spin" />
                              ) : (
                                'Активировать'
                              )}
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-destructive hover:text-destructive"
                              onClick={(e) => { e.stopPropagation(); handleDelete(plan.id); }}
                              disabled={deleteMutation.isPending}
                            >
                              {deleteMutation.isPending ? (
                                <Loader2 className="size-4 animate-spin" />
                              ) : (
                                <Trash2 className="size-4" />
                              )}
                            </Button>
                          </>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
