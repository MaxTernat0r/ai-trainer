'use client';

import Link from 'next/link';
import {
  Activity,
  AlertCircle,
  Calendar,
  Dumbbell,
  Plus,
  Radar,
  Sparkles,
  Target,
  Trophy,
  UtensilsCrossed,
  Weight,
  Zap,
} from 'lucide-react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { useDashboard } from '@/lib/queries/use-analytics';
import { useProfile } from '@/lib/queries/use-profile';
import { useWorkoutPlans } from '@/lib/queries/use-workouts';

function StatSkeleton() {
  return (
    <Card className="panel-reveal min-h-[120px] sm:min-h-[148px]">
      <CardContent className="flex h-full flex-col justify-between">
        <Skeleton className="size-10 rounded-lg" />
        <div className="flex flex-col gap-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-20" />
        </div>
      </CardContent>
    </Card>
  );
}

function getWorkoutPlural(count: number) {
  if (count % 10 === 1 && count % 100 !== 11) {
    return 'тренировка';
  }

  if (
    count % 10 >= 2
    && count % 10 <= 4
    && (count % 100 < 12 || count % 100 > 14)
  ) {
    return 'тренировки';
  }

  return 'тренировок';
}

function clampPercent(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)));
}

export default function DashboardPage() {
  const { data: dashboard, isLoading, isError } = useDashboard();
  const { data: profile } = useProfile();
  const { data: plans, isLoading: plansLoading } = useWorkoutPlans();

  const workoutsThisWeek = dashboard?.workouts_this_week ?? 0;
  const workoutPlural = getWorkoutPlural(workoutsThisWeek);
  const activePlan = plans?.find((plan) => plan.is_active) ?? null;
  const calories = dashboard?.calories_today ?? 0;
  const protein = dashboard?.protein_today ?? 0;
  const streak = dashboard?.streak_days ?? 0;
  const currentWeight = dashboard?.current_weight ?? profile?.weight_kg ?? null;

  const stats = [
    {
      title: 'Текущий вес',
      value: currentWeight != null ? String(currentWeight) : '-',
      suffix: currentWeight != null ? 'кг' : '',
      detail: dashboard?.weight_change_30d != null
        ? `${dashboard.weight_change_30d > 0 ? '+' : ''}${dashboard.weight_change_30d} кг за 30 дней`
        : 'ожидает следующий замер',
      icon: Weight,
      tone: 'text-zinc-200',
    },
    {
      title: 'Серия',
      value: String(streak),
      suffix: 'дней',
      detail: workoutsThisWeek > 0 ? `${workoutsThisWeek} ${workoutPlural} за неделю` : 'неделя еще свободна',
      icon: Trophy,
      tone: 'text-zinc-200',
    },
  ];

  const streamRows = [
    {
      id: '#WEEK',
      name: 'Тренировки на этой неделе',
      value: `${workoutsThisWeek} ${workoutPlural}`,
      status: workoutsThisWeek > 0 ? 'ACTIVE' : 'READY',
    },
    {
      id: '#PLAN',
      name: 'Активный план',
      value: activePlan?.title ?? 'Не выбран',
      status: activePlan ? 'ONLINE' : 'SETUP',
    },
    {
      id: '#FOOD',
      name: 'Питание сегодня',
      value: `${calories.toLocaleString('ru-RU')} ккал / ${protein} г`,
      status: calories > 0 || protein > 0 ? 'LOGGED' : 'EMPTY',
    },
  ];

  return (
    <div className="flex flex-col gap-3">
      {isError && (
        <Card className="border-destructive/35">
          <CardContent className="flex items-center gap-3">
            <AlertCircle className="size-5 text-destructive" />
            <p className="text-sm text-destructive">
              Не удалось загрузить данные. Попробуйте обновить страницу.
            </p>
          </CardContent>
        </Card>
      )}

      <Card className="panel-reveal min-h-[250px]">
        <CardHeader>
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="tactical-readout text-xs text-muted-foreground">
                tactical deployment
              </p>
              <CardTitle className="mt-2 text-xl">План на сейчас</CardTitle>
            </div>
            <Radar className="size-5 text-primary" />
          </div>
          <CardDescription>
            Текущий план и недельная нагрузка в одном контуре.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="glass-lane rounded-lg p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="tactical-readout text-[0.66rem] text-muted-foreground">
                  operation mode
                </p>
                <p className="mt-2 truncate text-lg font-semibold">
                  {plansLoading ? 'Загрузка...' : activePlan?.title ?? 'Создать тренировочный план'}
                </p>
              </div>
              <Target className="size-5 shrink-0 text-primary" />
            </div>
            <div className="mt-5 space-y-3">
              <div>
                <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
                  <span>Нагрузка недели</span>
                  <span>
                    {workoutsThisWeek} / {profile?.training_days_per_week ?? 4}
                  </span>
                </div>
                <Progress
                  value={clampPercent(
                    (workoutsThisWeek / (profile?.training_days_per_week ?? 4)) * 100
                  )}
                />
              </div>
              <div className="grid gap-2 sm:grid-cols-3">
                <Button asChild variant="outline" size="sm" className="priority-action">
                  <Link href="/workouts">
                    <Dumbbell className="size-4" />
                    Тренировки
                  </Link>
                </Button>
                <Button asChild variant="outline" size="sm" className="priority-action">
                  <Link href="/nutrition">
                    <UtensilsCrossed className="size-4" />
                    Питание
                  </Link>
                </Button>
                <Button asChild variant="outline" size="sm" className="priority-action">
                  <Link href="/chat">
                    <Sparkles className="size-4" />
                    Тренер
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <section className="grid gap-3 sm:grid-cols-2">
        {isLoading
          ? Array.from({ length: 2 }).map((_, i) => <StatSkeleton key={i} />)
          : stats.map((stat, index) => (
              <Card
                key={stat.title}
                className="panel-reveal min-h-[120px] sm:min-h-[148px]"
                style={{ animationDelay: `${120 + index * 55}ms` }}
              >
                <CardContent className="flex h-full flex-col justify-between">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex size-10 items-center justify-center rounded-lg border border-[#712031]/55 bg-black/18">
                      <stat.icon className={`size-5 ${stat.tone}`} />
                    </div>
                    <Zap className="size-4 text-primary/70" />
                  </div>
                  <div>
                    <p className="tactical-readout text-[0.66rem] text-muted-foreground">
                      {stat.title}
                    </p>
                    <p className="mt-2 text-2xl font-semibold sm:text-3xl">
                      {stat.value}
                      {stat.suffix && (
                        <span className="ml-1 text-sm font-normal text-muted-foreground">
                          {stat.suffix}
                        </span>
                      )}
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {stat.detail}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
      </section>

      <Card className="panel-reveal [animation-delay:340ms]">
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <CardTitle className="text-base">Instance stream</CardTitle>
              <CardDescription>
                Главное на сегодня без отдельного блока-заглушки.
              </CardDescription>
            </div>
            <Button asChild variant="outline" size="sm" className="priority-action">
              <Link href="/analytics">
                <Activity className="size-4" />
                Аналитика
              </Link>
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-hidden rounded-lg border border-[#712031]/55">
            <div className="hidden grid-cols-[0.28fr_1fr_0.58fr_0.32fr] gap-4 border-b border-[#712031]/55 bg-black/18 px-4 py-3 text-xs text-muted-foreground md:grid">
              <span>Instance ID</span>
              <span>Metric</span>
              <span>Value</span>
              <span>Status</span>
            </div>
            {streamRows.map((row) => (
              <div
                key={row.id}
                className="grid gap-2 border-b border-[#712031]/42 px-4 py-4 text-sm last:border-b-0 md:grid-cols-[0.28fr_1fr_0.58fr_0.32fr] md:gap-4"
              >
                <span className="tactical-readout text-[0.72rem] text-muted-foreground">
                  {row.id}
                </span>
                <span className="font-medium">{row.name}</span>
                <span className="text-muted-foreground">{row.value}</span>
                <span className="tactical-readout text-[0.68rem] text-primary">
                  {row.status}
                </span>
              </div>
            ))}
          </div>
          <div className="mt-4 flex flex-col gap-3 rounded-lg border border-dashed border-primary/28 bg-primary/[0.045] p-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex size-10 shrink-0 items-center justify-center rounded-lg border border-primary/30 bg-primary/12 text-primary">
                <Calendar className="size-5" />
              </div>
              <div>
                <p className="font-semibold">Следующий шаг</p>
                <p className="text-sm text-muted-foreground">
                  {activePlan
                    ? 'Откройте активный план и отметьте ближайшую тренировку.'
                    : 'Сгенерируйте план, чтобы запустить недельный цикл.'}
                </p>
              </div>
            </div>
            <Button asChild size="sm" className="priority-action">
              <Link href="/workouts">
                <Plus className="size-4" />
                Открыть
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
