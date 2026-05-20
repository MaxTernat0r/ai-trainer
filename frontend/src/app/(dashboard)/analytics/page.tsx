'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import {
  Scale,
  Ruler,
  Dumbbell,
  UtensilsCrossed,
  Flame,
  Beef,
  Droplets,
  Wheat,
  TrendingDown,
  TrendingUp,
  CalendarDays,
  Loader2,
  Plus,
  History,
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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  useWeightLogs,
  useLogWeight,
  useMeasurements,
  useLogMeasurement,
  useTrainedExercises,
  useExerciseProgress,
  useExerciseSessions,
  useCompletedSessions,
  useDashboard,
} from '@/lib/queries/use-analytics';
import {
  useDailySummary,
  useNutritionPlans,
} from '@/lib/queries/use-nutrition';

const MEASUREMENT_TYPES = [
  { value: 'chest', label: 'Грудь' },
  { value: 'waist', label: 'Талия' },
  { value: 'hips', label: 'Бёдра' },
  { value: 'bicep', label: 'Бицепс' },
  { value: 'thigh', label: 'Бедро' },
  { value: 'calf', label: 'Икра' },
  { value: 'neck', label: 'Шея' },
  { value: 'forearm', label: 'Предплечье' },
] as const;

function getMeasurementLabel(type: string): string {
  return MEASUREMENT_TYPES.find((m) => m.value === type)?.label ?? type;
}

export default function AnalyticsPage() {
  const [newWeight, setNewWeight] = useState('');
  const [weightPeriod, setWeightPeriod] = useState<'week' | 'month' | 'year' | 'all'>('month');
  const [logDate, setLogDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [measurementType, setMeasurementType] = useState('chest');
  const [measurementValue, setMeasurementValue] = useState('');
  const [measurementDate, setMeasurementDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const [selectedExerciseId, setSelectedExerciseId] = useState<string | null>(null);
  const todayString = useMemo(() => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }, []);

  // History tab state
  const [selectedEntryId, setSelectedEntryId] = useState<string>('');
  const [selectedHistoryExerciseId, setSelectedHistoryExerciseId] = useState<string>('');

  // Queries
  const { data: dashboard, isLoading: dashboardLoading } = useDashboard();
  const { data: weightLogs, isLoading: weightLoading } = useWeightLogs();
  const { data: measurementLogs, isLoading: measurementsLoading } = useMeasurements(measurementType);
  const { data: trainedExercises, isLoading: exercisesLoading } = useTrainedExercises();
  const effectiveSelectedExerciseId =
    selectedExerciseId ?? trainedExercises?.[0]?.exercise_id ?? null;
  const { data: exerciseProgress, isLoading: progressLoading } = useExerciseProgress(effectiveSelectedExerciseId);
  const { data: completedSessions, isLoading: historyLoading } = useCompletedSessions();
  const { data: nutritionSummary, isLoading: nutritionSummaryLoading } = useDailySummary(todayString);
  const { data: nutritionPlans, isLoading: nutritionPlansLoading } = useNutritionPlans();

  // Mutations
  const logWeightMutation = useLogWeight();
  const logMeasurementMutation = useLogMeasurement();
  const activeNutritionPlan = nutritionPlans?.find((plan) => plan.is_active);
  const nutritionTargets = {
    calories: activeNutritionPlan?.daily_calories ?? 2500,
    protein: activeNutritionPlan?.daily_protein_g ?? 180,
    fat: activeNutritionPlan?.daily_fat_g ?? 80,
    carbs: activeNutritionPlan?.daily_carbs_g ?? 280,
  };
  const nutritionTotals = nutritionSummary ?? {
    total_calories: 0,
    total_protein_g: 0,
    total_fat_g: 0,
    total_carbs_g: 0,
    meals_logged: 0,
  };
  const nutritionMetrics = [
    {
      label: 'Калории',
      current: Math.round(nutritionTotals.total_calories),
      target: nutritionTargets.calories,
      unit: 'ккал',
      icon: Flame,
    },
    {
      label: 'Белки',
      current: Math.round(nutritionTotals.total_protein_g),
      target: nutritionTargets.protein,
      unit: 'г',
      icon: Beef,
    },
    {
      label: 'Жиры',
      current: Math.round(nutritionTotals.total_fat_g),
      target: nutritionTargets.fat,
      unit: 'г',
      icon: Droplets,
    },
    {
      label: 'Углеводы',
      current: Math.round(nutritionTotals.total_carbs_g),
      target: nutritionTargets.carbs,
      unit: 'г',
      icon: Wheat,
    },
  ];

  // History tab: selected session and resolved exercise_id
  const selectedSession = useMemo(() => {
    if (!completedSessions || !selectedEntryId) return null;
    return completedSessions.find((s) => s.entry_id === selectedEntryId) ?? null;
  }, [completedSessions, selectedEntryId]);

  const historyExerciseGlobalId = useMemo(() => {
    if (!selectedSession || !selectedHistoryExerciseId) return null;
    return selectedSession.exercises.find(
      (e) => e.workout_exercise_id === selectedHistoryExerciseId
    )?.exercise_id ?? null;
  }, [selectedSession, selectedHistoryExerciseId]);

  // This query depends on historyExerciseGlobalId computed above
  const { data: historyExerciseSessions, isLoading: historyExerciseLoading } = useExerciseSessions(historyExerciseGlobalId);

  // History: filter sessions to only the selected entry's sets
  const historySetsChartData = useMemo(() => {
    if (!historyExerciseSessions || !selectedEntryId) return [];
    const match = historyExerciseSessions.find(
      (s) => s.scheduled_workout_id === selectedEntryId
    );
    if (!match) return [];
    return match.sets.map((s) => ({
      name: s.is_warmup ? `Р${s.set_number}` : `П${s.set_number}`,
      volume: (s.weight_kg ?? 0) * (s.reps_completed ?? 0),
    }));
  }, [historyExerciseSessions, selectedEntryId]);

  // Compute chart data from real weight logs, filtered by period
  const chartData = useMemo(() => {
    if (!weightLogs || weightLogs.length === 0) return [];
    const now = new Date();
    const cutoff = new Date();
    if (weightPeriod === 'week') cutoff.setDate(now.getDate() - 7);
    else if (weightPeriod === 'month') cutoff.setMonth(now.getMonth() - 1);
    else if (weightPeriod === 'year') cutoff.setFullYear(now.getFullYear() - 1);
    else cutoff.setFullYear(2000);

    return weightLogs
      .filter((entry) => new Date(entry.logged_at) >= cutoff)
      .map((entry) => ({
        date: new Date(entry.logged_at).toLocaleDateString('ru-RU', {
          day: 'numeric',
          month: 'short',
        }),
        weight: entry.weight_kg,
      }));
  }, [weightLogs, weightPeriod]);

  // Compute measurement chart data
  const measurementChartData = useMemo(() => {
    if (!measurementLogs || measurementLogs.length === 0) return [];
    return measurementLogs.map((entry) => ({
      date: new Date(entry.logged_at).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
      }),
      value: entry.value_cm,
    }));
  }, [measurementLogs]);

  // Exercise progress chart data (global best set per day)
  const progressChartData = useMemo(() => {
    if (!exerciseProgress || exerciseProgress.length === 0) return [];
    return exerciseProgress.map((p) => ({
      date: new Date(p.date).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
      }),
      weight: p.weight_kg ?? 0,
      reps: p.reps_completed ?? 0,
      volume: p.volume,
      session: p.session_name,
    }));
  }, [exerciseProgress]);

  const currentWeight = weightLogs && weightLogs.length > 0
    ? weightLogs[weightLogs.length - 1].weight_kg
    : dashboard?.current_weight ?? null;
  const startWeight = weightLogs && weightLogs.length > 0
    ? weightLogs[0].weight_kg
    : null;
  const weightChange = currentWeight !== null && startWeight !== null
    ? (currentWeight - startWeight).toFixed(1)
    : null;
  const isWeightDown = weightChange !== null && Number(weightChange) < 0;

  const handleLogWeight = () => {
    if (!newWeight) return;

    logWeightMutation.mutate(
      {
        weight_kg: Number(newWeight),
        logged_at: logDate,
      },
      {
        onSuccess: () => {
          toast.success('Вес записан');
          setNewWeight('');
        },
        onError: () => {
          toast.error('Не удалось записать вес');
        },
      }
    );
  };

  const handleLogMeasurement = () => {
    if (!measurementValue || !measurementType) return;

    logMeasurementMutation.mutate(
      {
        measurement_type: measurementType,
        value_cm: Number(measurementValue),
        logged_at: measurementDate,
      },
      {
        onSuccess: () => {
          toast.success('Замер записан');
          setMeasurementValue('');
        },
        onError: () => {
          toast.error('Не удалось записать замер');
        },
      }
    );
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Аналитика</h1>
        <p className="text-muted-foreground">
          Отслеживайте прогресс и анализируйте результаты
        </p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="weight" className="w-full">
        <div className="no-scrollbar -mx-1 overflow-x-auto px-1">
          <TabsList className="inline-flex w-max min-w-full sm:w-auto sm:min-w-0">
            <TabsTrigger value="weight" className="gap-1.5">
              <Scale className="size-4" />
              Вес
            </TabsTrigger>
            <TabsTrigger value="measurements" className="gap-1.5">
              <Ruler className="size-4" />
              Замеры
            </TabsTrigger>
            <TabsTrigger value="workouts" className="gap-1.5">
              <Dumbbell className="size-4" />
              Тренировки
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-1.5">
              <History className="size-4" />
              История
            </TabsTrigger>
            <TabsTrigger value="nutrition" className="gap-1.5">
              <UtensilsCrossed className="size-4" />
              Питание
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Weight tab */}
        <TabsContent value="weight" className="mt-6">
          <div className="flex flex-col gap-6">
            {/* Stats row */}
            <div className="grid gap-4 sm:grid-cols-3">
              <Card className="border-border/50">
                <CardContent className="flex items-center gap-3 pt-6">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-primary/12">
                    <Scale className="size-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Текущий вес</p>
                    {weightLoading || dashboardLoading ? (
                      <Skeleton className="h-7 w-20" />
                    ) : (
                      <p className="text-xl font-bold">
                        {currentWeight !== null ? `${currentWeight} кг` : '-- кг'}
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
              <Card className="border-border/50">
                <CardContent className="flex items-center gap-3 pt-6">
                  <div className={`flex size-10 items-center justify-center rounded-lg ${isWeightDown ? 'bg-primary/12' : 'bg-red-500/10'}`}>
                    {isWeightDown ? (
                      <TrendingDown className="size-5 text-primary" />
                    ) : (
                      <TrendingUp className="size-5 text-primary" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Изменение</p>
                    {weightLoading ? (
                      <Skeleton className="h-7 w-20" />
                    ) : (
                      <p className="text-xl font-bold">
                        {weightChange !== null ? `${weightChange} кг` : '-- кг'}
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
              <Card className="border-border/50">
                <CardContent className="flex items-center gap-3 pt-6">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-white/[0.055]">
                    <CalendarDays className="size-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Записей
                    </p>
                    {weightLoading ? (
                      <Skeleton className="h-7 w-12" />
                    ) : (
                      <p className="text-xl font-bold">{weightLogs?.length ?? 0}</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Log weight form */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Записать вес</CardTitle>
                <CardDescription>
                  Регулярно записывайте вес для отслеживания прогресса
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="weight">Вес (кг)</Label>
                    <Input
                      id="weight"
                      type="number"
                      step="0.1"
                      placeholder="78.5"
                      value={newWeight}
                      onChange={(e) => setNewWeight(e.target.value)}
                      className="w-full sm:w-32"
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="date">Дата</Label>
                    <Input
                      id="date"
                      type="date"
                      value={logDate}
                      onChange={(e) => setLogDate(e.target.value)}
                      className="w-full sm:w-40"
                    />
                  </div>
                  <Button
                    className="priority-action"
                    onClick={handleLogWeight}
                    disabled={!newWeight || logWeightMutation.isPending}
                  >
                    {logWeightMutation.isPending ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Plus className="size-4" />
                    )}
                    Записать
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Chart */}
            <Card className="border-border/50">
              <CardHeader>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <CardTitle>Динамика веса</CardTitle>
                    <CardDescription>
                      Изменение вашего веса по повторным замерам
                    </CardDescription>
                  </div>
                  <div className="flex gap-1">
                    {([['week', 'Неделя'], ['month', 'Месяц'], ['year', 'Год'], ['all', 'Всё']] as const).map(([val, label]) => (
                      <Button
                        key={val}
                        variant={weightPeriod === val ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setWeightPeriod(val)}
                        className="text-xs"
                      >
                        {label}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {weightLoading ? (
                  <Skeleton className="h-72 w-full rounded-lg" />
                ) : chartData.length === 0 ? (
                  <div className="flex h-72 items-center justify-center">
                    <p className="text-sm text-muted-foreground">
                      Добавьте новый замер, чтобы построить график динамики.
                    </p>
                  </div>
                ) : (
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={chartData}
                        margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                        <XAxis
                          dataKey="date"
                          className="text-xs"
                          tick={{ fill: 'hsl(var(--muted-foreground))' }}
                        />
                        <YAxis
                          domain={['auto', 'auto']}
                          className="text-xs"
                          tick={{ fill: 'hsl(var(--muted-foreground))' }}
                          tickFormatter={(value: number) => `${value} кг`}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'hsl(var(--popover))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px',
                            color: 'hsl(var(--popover-foreground))',
                          }}
                          formatter={(value) => [`${value} кг`, 'Вес']}
                        />
                        <Line
                          type="monotone"
                          dataKey="weight"
                          stroke="#ff0030"
                          strokeWidth={2}
                          dot={{ fill: '#ff0030', strokeWidth: 2, r: 4 }}
                          activeDot={{ r: 6 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>

          </div>
        </TabsContent>

        {/* Measurements tab */}
        <TabsContent value="measurements" className="mt-6">
          <div className="flex flex-col gap-6">
            {/* Measurement type selector */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Замеры тела</CardTitle>
                <CardDescription>
                  Отслеживайте объёмы различных частей тела
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {MEASUREMENT_TYPES.map((mt) => (
                    <Button
                      key={mt.value}
                      variant={measurementType === mt.value ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setMeasurementType(mt.value)}
                    >
                      {mt.label}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Log measurement form */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Записать замер</CardTitle>
                <CardDescription>
                  Выберите тип замера и введите значение в сантиметрах
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
                  <div className="flex flex-col gap-2">
                    <Label>Тип замера</Label>
                    <Select value={measurementType} onValueChange={setMeasurementType}>
                      <SelectTrigger className="w-full sm:w-40">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {MEASUREMENT_TYPES.map((mt) => (
                          <SelectItem key={mt.value} value={mt.value}>
                            {mt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="measurement-value">Значение (см)</Label>
                    <Input
                      id="measurement-value"
                      type="number"
                      step="0.1"
                      placeholder="90.5"
                      value={measurementValue}
                      onChange={(e) => setMeasurementValue(e.target.value)}
                      className="w-full sm:w-32"
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="measurement-date">Дата</Label>
                    <Input
                      id="measurement-date"
                      type="date"
                      value={measurementDate}
                      onChange={(e) => setMeasurementDate(e.target.value)}
                      className="w-full sm:w-40"
                    />
                  </div>
                  <Button
                    className="priority-action"
                    onClick={handleLogMeasurement}
                    disabled={!measurementValue || logMeasurementMutation.isPending}
                  >
                    {logMeasurementMutation.isPending ? (
                      <Loader2 className="size-4 animate-spin" />
                    ) : (
                      <Plus className="size-4" />
                    )}
                    Записать
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Measurement chart */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>
                  {getMeasurementLabel(measurementType)} - динамика
                </CardTitle>
                <CardDescription>
                  Изменение замеров за всё время
                </CardDescription>
              </CardHeader>
              <CardContent>
                {measurementsLoading ? (
                  <Skeleton className="h-72 w-full rounded-lg" />
                ) : measurementChartData.length === 0 ? (
                  <div className="flex h-72 items-center justify-center">
                    <p className="text-sm text-muted-foreground">
                      Нет данных для «{getMeasurementLabel(measurementType)}». Запишите первый замер выше.
                    </p>
                  </div>
                ) : (
                  <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={measurementChartData}
                        margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                        <XAxis
                          dataKey="date"
                          className="text-xs"
                          tick={{ fill: 'hsl(var(--muted-foreground))' }}
                        />
                        <YAxis
                          domain={['auto', 'auto']}
                          className="text-xs"
                          tick={{ fill: 'hsl(var(--muted-foreground))' }}
                          tickFormatter={(value: number) => `${value} см`}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'hsl(var(--popover))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px',
                            color: 'hsl(var(--popover-foreground))',
                          }}
                          formatter={(value) => [`${value} см`, getMeasurementLabel(measurementType)]}
                        />
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke="hsl(var(--primary))"
                          strokeWidth={2}
                          dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
                          activeDot={{ r: 6 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent measurements table */}
            {measurementLogs && measurementLogs.length > 0 && (
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle>
                    Последние записи - {getMeasurementLabel(measurementType)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-col gap-2">
                    {measurementLogs.slice(-10).reverse().map((log) => (
                      <div
                        key={log.id}
                        className="flex items-center justify-between rounded-lg border border-border/50 px-4 py-2"
                      >
                        <span className="text-sm text-muted-foreground">
                          {new Date(log.logged_at).toLocaleDateString('ru-RU', {
                            day: 'numeric',
                            month: 'long',
                            year: 'numeric',
                          })}
                        </span>
                        <Badge variant="secondary">{log.value_cm} см</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Workouts tab */}
        <TabsContent value="workouts" className="mt-6">
          {exercisesLoading ? (
            <Skeleton className="h-96 w-full rounded-lg" />
          ) : !trainedExercises || trainedExercises.length === 0 ? (
            <Card className="border-border/50">
              <CardContent className="flex flex-col items-center justify-center gap-4 py-16">
                <div className="flex size-16 items-center justify-center rounded-full bg-muted">
                  <Dumbbell className="size-8 text-muted-foreground" />
                </div>
                <div className="text-center">
                  <h3 className="text-lg font-semibold">
                    Статистика тренировок
                  </h3>
                  <p className="mt-1 max-w-md text-sm text-muted-foreground">
                    Статистика тренировок будет доступна после начала занятий.
                    Начните тренироваться, и здесь появятся графики прогресса.
                  </p>
                </div>
                <Button variant="outline" asChild>
                  <Link href="/workouts">Перейти к тренировкам</Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="flex flex-col gap-6">
              {/* Exercise selector */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle>Выберите упражнение</CardTitle>
                  <CardDescription>
                    Просматривайте прогресс по каждому упражнению
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Select
                    value={effectiveSelectedExerciseId ?? ''}
                    onValueChange={setSelectedExerciseId}
                  >
                    <SelectTrigger className="w-full sm:w-80">
                      <SelectValue placeholder="Выберите упражнение" />
                    </SelectTrigger>
                    <SelectContent>
                      {trainedExercises.map((ex) => (
                        <SelectItem key={ex.exercise_id} value={ex.exercise_id}>
                          {ex.exercise_name_ru}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>

              {effectiveSelectedExerciseId && (
                <>
                  {/* Global progress chart */}
                  <Card className="border-border/50">
                    <CardHeader>
                      <CardTitle>Прогресс по весу</CardTitle>
                      <CardDescription>
                        Лучший подход за каждую тренировку (вес, кг)
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {progressLoading ? (
                        <Skeleton className="h-72 w-full rounded-lg" />
                      ) : progressChartData.length === 0 ? (
                        <div className="flex h-72 items-center justify-center">
                          <p className="text-sm text-muted-foreground">
                            Нет данных по этому упражнению
                          </p>
                        </div>
                      ) : (
                        <div className="h-72 w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart
                              data={progressChartData}
                              margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                              <XAxis
                                dataKey="date"
                                className="text-xs"
                                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                              />
                              <YAxis
                                domain={['auto', 'auto']}
                                className="text-xs"
                                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                                tickFormatter={(v: number) => `${v} кг`}
                              />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: 'hsl(var(--popover))',
                                  border: '1px solid hsl(var(--border))',
                                  borderRadius: '8px',
                                  color: 'hsl(var(--popover-foreground))',
                                }}
                                formatter={(value, name) => {
                                  if (name === 'weight') return [`${value} кг`, 'Вес'];
                                  if (name === 'reps') return [`${value}`, 'Повторений'];
                                  return [`${value}`, String(name)];
                                }}
                              />
                              <Line
                                type="monotone"
                                dataKey="weight"
                                stroke="hsl(var(--primary))"
                                strokeWidth={2}
                                dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
                                activeDot={{ r: 6 }}
                                name="weight"
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Volume progress chart */}
                  <Card className="border-border/50">
                    <CardHeader>
                      <CardTitle>Прогресс по объёму</CardTitle>
                      <CardDescription>
                        Объём лучшего подхода (вес x повторения) за каждую тренировку
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {progressLoading ? (
                        <Skeleton className="h-72 w-full rounded-lg" />
                      ) : progressChartData.length === 0 ? (
                        <div className="flex h-72 items-center justify-center">
                          <p className="text-sm text-muted-foreground">
                            Нет данных
                          </p>
                        </div>
                      ) : (
                        <div className="h-72 w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart
                              data={progressChartData}
                              margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                              <XAxis
                                dataKey="date"
                                className="text-xs"
                                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                              />
                              <YAxis
                                domain={['auto', 'auto']}
                                className="text-xs"
                                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                              />
                              <Tooltip
                                contentStyle={{
                                  backgroundColor: 'hsl(var(--popover))',
                                  border: '1px solid hsl(var(--border))',
                                  borderRadius: '8px',
                                  color: 'hsl(var(--popover-foreground))',
                                }}
                                formatter={(value) => [`${value} кг`, 'Объём']}
                              />
                              <Line
                                type="monotone"
                                dataKey="volume"
                                stroke="#ff0030"
                                strokeWidth={2}
                                dot={{ fill: '#ff0030', strokeWidth: 2, r: 4 }}
                                activeDot={{ r: 6 }}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                </>
              )}
            </div>
          )}
        </TabsContent>

        {/* History tab */}
        <TabsContent value="history" className="mt-6">
          {historyLoading ? (
            <Skeleton className="h-96 w-full rounded-lg" />
          ) : !completedSessions || completedSessions.length === 0 ? (
            <Card className="border-border/50">
              <CardContent className="flex flex-col items-center justify-center gap-4 py-16">
                <div className="flex size-16 items-center justify-center rounded-full bg-muted">
                  <History className="size-8 text-muted-foreground" />
                </div>
                <div className="text-center">
                  <h3 className="text-lg font-semibold">
                    История тренировок
                  </h3>
                  <p className="mt-1 max-w-md text-sm text-muted-foreground">
                    Здесь будет история выполненных тренировок.
                    Начните тренироваться, и данные появятся автоматически.
                  </p>
                </div>
                <Button variant="outline" asChild>
                  <Link href="/workouts">Перейти к тренировкам</Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="flex flex-col gap-6">
              {/* Session selector */}
              <Card className="border-border/50">
                <CardHeader>
                  <CardTitle>Выберите тренировку</CardTitle>
                  <CardDescription>
                    Просмотрите подходы по каждому упражнению в конкретной тренировке
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Select
                    value={selectedEntryId}
                    onValueChange={(val) => {
                      setSelectedEntryId(val);
                      setSelectedHistoryExerciseId('');
                    }}
                  >
                    <SelectTrigger className="w-full sm:w-96">
                      <SelectValue placeholder="Выберите тренировку" />
                    </SelectTrigger>
                    <SelectContent>
                      {completedSessions.map((s) => (
                        <SelectItem key={s.entry_id} value={s.entry_id}>
                          {s.session_name} — {new Date(s.scheduled_date).toLocaleDateString('ru-RU', {
                            day: 'numeric',
                            month: 'long',
                            year: 'numeric',
                          })}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>

              {/* Exercise selector within session */}
              {selectedSession && (
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Упражнения</CardTitle>
                    <CardDescription>
                      {selectedSession.session_name} — {new Date(selectedSession.scheduled_date).toLocaleDateString('ru-RU', {
                        day: 'numeric',
                        month: 'long',
                      })}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {selectedSession.exercises.map((ex) => (
                        <Button
                          key={ex.workout_exercise_id}
                          variant={selectedHistoryExerciseId === ex.workout_exercise_id ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setSelectedHistoryExerciseId(ex.workout_exercise_id)}
                        >
                          {ex.exercise_name_ru} ({ex.sets_count})
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Volume per set chart */}
              {selectedHistoryExerciseId && (
                <Card className="border-border/50">
                  <CardHeader>
                    <CardTitle>Объём по подходам</CardTitle>
                    <CardDescription>
                      Вес × повторения (кг) для каждого подхода
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {historyExerciseLoading ? (
                      <Skeleton className="h-64 w-full rounded-lg" />
                    ) : historySetsChartData.length === 0 ? (
                      <div className="flex h-64 items-center justify-center">
                        <p className="text-sm text-muted-foreground">
                          Нет данных по подходам
                        </p>
                      </div>
                    ) : (
                      <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart
                            data={historySetsChartData}
                            margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                            <XAxis
                              dataKey="name"
                              className="text-xs"
                              tick={{ fill: 'hsl(var(--muted-foreground))' }}
                            />
                            <YAxis
                              domain={['auto', 'auto']}
                              className="text-xs"
                              tick={{ fill: 'hsl(var(--muted-foreground))' }}
                              tickFormatter={(v: number) => `${v} кг`}
                            />
                            <Tooltip
                              contentStyle={{
                                backgroundColor: 'hsl(var(--popover))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '8px',
                                color: 'hsl(var(--popover-foreground))',
                              }}
                              formatter={(value) => [`${value} кг`, 'Объём']}
                            />
                            <Line
                              type="monotone"
                              dataKey="volume"
                              stroke="#ff0030"
                              strokeWidth={2}
                              dot={{ fill: '#ff0030', strokeWidth: 2, r: 4 }}
                              activeDot={{ r: 6 }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </TabsContent>

        {/* Nutrition tab */}
        <TabsContent value="nutrition" className="mt-6">
          <div className="flex flex-col gap-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {nutritionSummaryLoading || nutritionPlansLoading
                ? Array.from({ length: 4 }).map((_, index) => (
                    <Card key={index} className="border-border/50">
                      <CardContent className="pt-6">
                        <Skeleton className="h-5 w-24" />
                        <Skeleton className="mt-4 h-8 w-28" />
                        <Skeleton className="mt-4 h-2 w-full" />
                      </CardContent>
                    </Card>
                  ))
                : nutritionMetrics.map((metric) => {
                    const percentage = metric.target > 0
                      ? Math.min(100, Math.round((metric.current / metric.target) * 100))
                      : 0;
                    const Icon = metric.icon;

                    return (
                      <Card key={metric.label} className="border-border/50">
                        <CardContent className="pt-6">
                          <div className="flex items-center justify-between gap-3">
                            <div>
                              <p className="text-sm text-muted-foreground">{metric.label}</p>
                              <p className="mt-1 text-2xl font-bold">
                                {metric.current}
                                <span className="ml-1 text-sm font-normal text-muted-foreground">
                                  / {metric.target} {metric.unit}
                                </span>
                              </p>
                            </div>
                            <div className="flex size-10 items-center justify-center rounded-full bg-primary/10">
                              <Icon className="size-5 text-primary" />
                            </div>
                          </div>
                          <Progress value={percentage} className="mt-4 h-2" />
                          <p className="mt-2 text-xs text-muted-foreground">
                            {percentage}% дневной цели
                          </p>
                        </CardContent>
                      </Card>
                    );
                  })}
            </div>

            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Питание сегодня</CardTitle>
                <CardDescription>
                  {activeNutritionPlan
                    ? `Цели из активного плана: ${activeNutritionPlan.title}`
                    : 'Цели по умолчанию до активации плана питания'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex size-10 items-center justify-center rounded-full bg-muted">
                      <UtensilsCrossed className="size-5 text-muted-foreground" />
                    </div>
                    <div>
                      <p className="text-sm font-medium">
                        Записано приёмов пищи: {nutritionTotals.meals_logged}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Дата: {new Date(`${todayString}T00:00:00`).toLocaleDateString('ru-RU', {
                          day: 'numeric',
                          month: 'long',
                          year: 'numeric',
                        })}
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" asChild>
                    <Link href="/nutrition">Открыть дневник питания</Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
