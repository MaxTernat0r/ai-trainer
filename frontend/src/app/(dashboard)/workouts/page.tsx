'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  Dumbbell,
  Plus,
  Calendar,
  Clock,
  ChevronRight,
  Sparkles,
  CheckCircle2,
  Zap,
} from 'lucide-react';
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
import type { WorkoutPlan, WorkoutPlanBrief } from '@/types/workout';

// --- Mock data ---
const mockActivePlan: WorkoutPlan = {
  id: 'plan-1',
  title: 'Программа набора массы',
  description: 'Классическая программа Push/Pull/Legs для набора мышечной массы',
  goal: 'muscle_gain',
  difficulty: 'intermediate',
  duration_weeks: 8,
  days_per_week: 4,
  is_ai_generated: true,
  is_active: true,
  sessions: [
    {
      id: 's1',
      day_number: 1,
      name: 'Push Day (Грудь, Плечи, Трицепс)',
      notes: null,
      order_index: 0,
      exercises: [
        { id: 'e1', exercise_id: 'ex1', exercise_name: 'Bench Press', exercise_name_ru: 'Жим штанги лёжа', order_index: 0, target_sets: 4, target_reps: '8-10', target_rest_seconds: 120, notes: null, logged_sets: [] },
        { id: 'e2', exercise_id: 'ex2', exercise_name: 'Overhead Press', exercise_name_ru: 'Жим штанги стоя', order_index: 1, target_sets: 3, target_reps: '10-12', target_rest_seconds: 90, notes: null, logged_sets: [] },
        { id: 'e3', exercise_id: 'ex3', exercise_name: 'Incline Dumbbell Press', exercise_name_ru: 'Жим гантелей на наклонной скамье', order_index: 2, target_sets: 3, target_reps: '10-12', target_rest_seconds: 90, notes: null, logged_sets: [] },
        { id: 'e4', exercise_id: 'ex4', exercise_name: 'Lateral Raises', exercise_name_ru: 'Разводка гантелей в стороны', order_index: 3, target_sets: 3, target_reps: '12-15', target_rest_seconds: 60, notes: null, logged_sets: [] },
        { id: 'e5', exercise_id: 'ex5', exercise_name: 'Triceps Pushdown', exercise_name_ru: 'Разгибание рук на блоке', order_index: 4, target_sets: 3, target_reps: '12-15', target_rest_seconds: 60, notes: null, logged_sets: [] },
      ],
    },
    {
      id: 's2',
      day_number: 2,
      name: 'Pull Day (Спина, Бицепс)',
      notes: null,
      order_index: 1,
      exercises: [
        { id: 'e6', exercise_id: 'ex6', exercise_name: 'Deadlift', exercise_name_ru: 'Становая тяга', order_index: 0, target_sets: 4, target_reps: '6-8', target_rest_seconds: 180, notes: null, logged_sets: [] },
        { id: 'e7', exercise_id: 'ex7', exercise_name: 'Pull-ups', exercise_name_ru: 'Подтягивания', order_index: 1, target_sets: 4, target_reps: '8-10', target_rest_seconds: 120, notes: null, logged_sets: [] },
        { id: 'e8', exercise_id: 'ex8', exercise_name: 'Barbell Row', exercise_name_ru: 'Тяга штанги в наклоне', order_index: 2, target_sets: 3, target_reps: '10-12', target_rest_seconds: 90, notes: null, logged_sets: [] },
        { id: 'e9', exercise_id: 'ex9', exercise_name: 'Bicep Curls', exercise_name_ru: 'Сгибание рук со штангой', order_index: 3, target_sets: 3, target_reps: '10-12', target_rest_seconds: 60, notes: null, logged_sets: [] },
      ],
    },
    {
      id: 's3',
      day_number: 3,
      name: 'Legs Day (Ноги)',
      notes: null,
      order_index: 2,
      exercises: [
        { id: 'e10', exercise_id: 'ex10', exercise_name: 'Squat', exercise_name_ru: 'Приседания со штангой', order_index: 0, target_sets: 4, target_reps: '8-10', target_rest_seconds: 180, notes: null, logged_sets: [] },
        { id: 'e11', exercise_id: 'ex11', exercise_name: 'Romanian Deadlift', exercise_name_ru: 'Румынская тяга', order_index: 1, target_sets: 3, target_reps: '10-12', target_rest_seconds: 120, notes: null, logged_sets: [] },
        { id: 'e12', exercise_id: 'ex12', exercise_name: 'Leg Press', exercise_name_ru: 'Жим ногами', order_index: 2, target_sets: 3, target_reps: '12-15', target_rest_seconds: 90, notes: null, logged_sets: [] },
        { id: 'e13', exercise_id: 'ex13', exercise_name: 'Calf Raises', exercise_name_ru: 'Подъёмы на носки', order_index: 3, target_sets: 4, target_reps: '15-20', target_rest_seconds: 60, notes: null, logged_sets: [] },
      ],
    },
    {
      id: 's4',
      day_number: 4,
      name: 'Upper Body (Верх тела)',
      notes: null,
      order_index: 3,
      exercises: [
        { id: 'e14', exercise_id: 'ex14', exercise_name: 'Dumbbell Press', exercise_name_ru: 'Жим гантелей лёжа', order_index: 0, target_sets: 3, target_reps: '10-12', target_rest_seconds: 90, notes: null, logged_sets: [] },
        { id: 'e15', exercise_id: 'ex15', exercise_name: 'Cable Row', exercise_name_ru: 'Тяга нижнего блока', order_index: 1, target_sets: 3, target_reps: '10-12', target_rest_seconds: 90, notes: null, logged_sets: [] },
        { id: 'e16', exercise_id: 'ex16', exercise_name: 'Arnold Press', exercise_name_ru: 'Жим Арнольда', order_index: 2, target_sets: 3, target_reps: '10-12', target_rest_seconds: 90, notes: null, logged_sets: [] },
      ],
    },
  ],
};

const mockAllPlans: WorkoutPlanBrief[] = [
  {
    id: 'plan-1',
    title: 'Программа набора массы',
    goal: 'muscle_gain',
    difficulty: 'intermediate',
    duration_weeks: 8,
    days_per_week: 4,
    is_ai_generated: true,
    is_active: true,
  },
  {
    id: 'plan-2',
    title: 'Жиросжигание: Full Body',
    goal: 'fat_loss',
    difficulty: 'beginner',
    duration_weeks: 6,
    days_per_week: 3,
    is_ai_generated: true,
    is_active: false,
  },
  {
    id: 'plan-3',
    title: 'Силовая программа 5x5',
    goal: 'strength',
    difficulty: 'advanced',
    duration_weeks: 12,
    days_per_week: 3,
    is_ai_generated: false,
    is_active: false,
  },
];

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

export default function WorkoutsPage() {
  const [hasActivePlan] = useState(true);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [weeks, setWeeks] = useState([8]);
  const [daysPerWeek, setDaysPerWeek] = useState('4');
  const [periodization, setPeriodization] = useState('linear');

  const activePlan = hasActivePlan ? mockActivePlan : null;

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

              <Button className="w-full" onClick={() => setSheetOpen(false)}>
                <Sparkles className="size-4" />
                Сгенерировать программу
              </Button>
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* No active plan CTA */}
      {!activePlan && (
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
      {activePlan && (
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
                    <CardDescription>{activePlan.description}</CardDescription>
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
                    className={difficultyColors[activePlan.difficulty]}
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
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Dumbbell className="size-4" />
                  <span>{activePlan.sessions.length} тренировок</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sessions grid */}
          <div>
            <h2 className="mb-4 text-lg font-semibold">Тренировочные дни</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {activePlan.sessions.map((session) => (
                <Link key={session.id} href={`/workouts/${session.id}`}>
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
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        </>
      )}

      {/* All plans */}
      <Separator />
      <div>
        <h2 className="mb-4 text-lg font-semibold">Все программы</h2>
        <div className="flex flex-col gap-3">
          {mockAllPlans.map((plan) => (
            <Card
              key={plan.id}
              className={`border-border/50 transition-colors ${
                plan.is_active ? 'ring-2 ring-primary/20' : ''
              }`}
            >
              <CardContent className="flex items-center justify-between pt-6">
                <div className="flex items-center gap-4">
                  <div
                    className={`flex size-10 items-center justify-center rounded-lg ${
                      plan.is_active ? 'bg-primary/10' : 'bg-muted'
                    }`}
                  >
                    <Dumbbell
                      className={`size-5 ${
                        plan.is_active ? 'text-primary' : 'text-muted-foreground'
                      }`}
                    />
                  </div>
                  <div>
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
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className={difficultyColors[plan.difficulty]}
                  >
                    {difficultyLabels[plan.difficulty] ?? plan.difficulty}
                  </Badge>
                  {!plan.is_active && (
                    <Button variant="outline" size="sm">
                      Активировать
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
