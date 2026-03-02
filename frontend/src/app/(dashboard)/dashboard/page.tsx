'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Flame,
  Beef,
  Weight,
  Trophy,
  Dumbbell,
  UtensilsCrossed,
  Plus,
  TrendingDown,
  TrendingUp,
  Calendar,
  AlertCircle,
} from 'lucide-react';
import Link from 'next/link';
import { useDashboard } from '@/lib/queries/use-analytics';

function StatSkeleton() {
  return (
    <Card className="border-border/50">
      <CardContent className="flex items-center gap-4 pt-6">
        <Skeleton className="size-12 shrink-0 rounded-lg" />
        <div className="flex flex-col gap-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-7 w-20" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { data: dashboard, isLoading, isError } = useDashboard();

  const stats = [
    {
      title: 'Калории сегодня',
      value: dashboard?.calories_today ?? 0,
      formatted: (dashboard?.calories_today ?? 0).toLocaleString('ru-RU'),
      suffix: 'ккал',
      icon: Flame,
      color: 'text-orange-500',
      bgColor: 'bg-orange-500/10',
    },
    {
      title: 'Белок сегодня',
      value: dashboard?.protein_today ?? 0,
      formatted: String(dashboard?.protein_today ?? 0),
      suffix: 'г',
      icon: Beef,
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
    },
    {
      title: 'Текущий вес',
      value: dashboard?.current_weight,
      formatted: dashboard?.current_weight != null
        ? String(dashboard.current_weight)
        : '\u2014',
      suffix: dashboard?.current_weight != null ? 'кг' : '',
      icon: Weight,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Серия тренировок',
      value: dashboard?.streak_days ?? 0,
      formatted: String(dashboard?.streak_days ?? 0),
      suffix: 'дней',
      icon: Trophy,
      color: 'text-amber-500',
      bgColor: 'bg-amber-500/10',
    },
  ];

  const secondaryStats = [
    {
      title: 'Тренировок на этой неделе',
      value: dashboard?.workouts_this_week ?? 0,
      formatted: String(dashboard?.workouts_this_week ?? 0),
      icon: Calendar,
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    ...(dashboard?.weight_change_30d != null
      ? [
          {
            title: 'Изменение веса за 30 дней',
            value: dashboard.weight_change_30d,
            formatted: `${dashboard.weight_change_30d > 0 ? '+' : ''}${dashboard.weight_change_30d} кг`,
            icon: dashboard.weight_change_30d >= 0 ? TrendingUp : TrendingDown,
            color:
              dashboard.weight_change_30d >= 0
                ? 'text-green-500'
                : 'text-blue-500',
            bgColor:
              dashboard.weight_change_30d >= 0
                ? 'bg-green-500/10'
                : 'bg-blue-500/10',
          },
        ]
      : []),
  ];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Главная</h1>
        <p className="text-muted-foreground">
          Обзор вашей активности и прогресса
        </p>
      </div>

      {/* Error state */}
      {isError && (
        <Card className="border-destructive/30">
          <CardContent className="flex items-center gap-3 pt-6">
            <AlertCircle className="size-5 text-destructive" />
            <p className="text-sm text-destructive">
              Не удалось загрузить данные. Попробуйте обновить страницу.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => <StatSkeleton key={i} />)
          : stats.map((stat) => (
              <Card key={stat.title} className="border-border/50">
                <CardContent className="flex items-center gap-4 pt-6">
                  <div
                    className={`flex size-12 shrink-0 items-center justify-center rounded-lg ${stat.bgColor}`}
                  >
                    <stat.icon className={`size-6 ${stat.color}`} />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold">
                      {stat.formatted}{' '}
                      {stat.suffix && (
                        <span className="text-sm font-normal text-muted-foreground">
                          {stat.suffix}
                        </span>
                      )}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ))}
      </div>

      {/* Secondary stats */}
      {!isLoading && secondaryStats.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2">
          {secondaryStats.map((stat) => (
            <Card key={stat.title} className="border-border/50">
              <CardContent className="flex items-center gap-4 pt-6">
                <div
                  className={`flex size-12 shrink-0 items-center justify-center rounded-lg ${stat.bgColor}`}
                >
                  <stat.icon className={`size-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                  <p className="text-2xl font-bold">{stat.formatted}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Action cards */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border/50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10">
                <Dumbbell className="size-5 text-primary" />
              </div>
              <div>
                <CardTitle>Сегодняшняя тренировка</CardTitle>
                <CardDescription>
                  У вас пока нет активной программы тренировок
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex min-h-[120px] flex-col items-center justify-center gap-4 rounded-lg border border-dashed border-border/70 p-6 text-center">
              <p className="text-sm text-muted-foreground">
                Создайте персональную программу тренировок с помощью ИИ
              </p>
              <Button asChild>
                <Link href="/workouts">
                  <Plus className="size-4" />
                  Создать программу
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-lg bg-green-500/10">
                <UtensilsCrossed className="size-5 text-green-500" />
              </div>
              <div>
                <CardTitle>План питания</CardTitle>
                <CardDescription>
                  У вас пока нет активного плана питания
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex min-h-[120px] flex-col items-center justify-center gap-4 rounded-lg border border-dashed border-border/70 p-6 text-center">
              <p className="text-sm text-muted-foreground">
                Получите индивидуальный план питания, подобранный ИИ
              </p>
              <Button asChild>
                <Link href="/nutrition">
                  <Plus className="size-4" />
                  Создать программу
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
