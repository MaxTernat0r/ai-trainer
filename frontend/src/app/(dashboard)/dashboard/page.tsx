'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Flame,
  Beef,
  Weight,
  Trophy,
  Dumbbell,
  UtensilsCrossed,
  Plus,
} from 'lucide-react';
import Link from 'next/link';

const stats = [
  {
    title: 'Калории сегодня',
    value: '1 850',
    suffix: 'ккал',
    icon: Flame,
    color: 'text-orange-500',
    bgColor: 'bg-orange-500/10',
  },
  {
    title: 'Белок сегодня',
    value: '120',
    suffix: 'г',
    icon: Beef,
    color: 'text-red-500',
    bgColor: 'bg-red-500/10',
  },
  {
    title: 'Текущий вес',
    value: '78.5',
    suffix: 'кг',
    icon: Weight,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
  },
  {
    title: 'Серия тренировок',
    value: '12',
    suffix: 'дней',
    icon: Trophy,
    color: 'text-amber-500',
    bgColor: 'bg-amber-500/10',
  },
];

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Главная</h1>
        <p className="text-muted-foreground">
          Обзор вашей активности и прогресса
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title} className="border-border/50">
            <CardContent className="flex items-center gap-4 pt-6">
              <div
                className={`flex size-12 shrink-0 items-center justify-center rounded-lg ${stat.bgColor}`}
              >
                <stat.icon className={`size-6 ${stat.color}`} />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{stat.title}</p>
                <p className="text-2xl font-bold">
                  {stat.value}{' '}
                  <span className="text-sm font-normal text-muted-foreground">
                    {stat.suffix}
                  </span>
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

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
