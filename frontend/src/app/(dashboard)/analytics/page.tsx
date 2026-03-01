'use client';

import { useState } from 'react';
import {
  Scale,
  Ruler,
  Dumbbell,
  UtensilsCrossed,
  TrendingDown,
  CalendarDays,
  Clock,
} from 'lucide-react';
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
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { WeightLog } from '@/types/analytics';

// --- Mock data ---
const mockWeightData: WeightLog[] = [
  { id: '1', weight_kg: 82.5, logged_at: '2026-01-01' },
  { id: '2', weight_kg: 82.1, logged_at: '2026-01-08' },
  { id: '3', weight_kg: 81.8, logged_at: '2026-01-15' },
  { id: '4', weight_kg: 81.3, logged_at: '2026-01-22' },
  { id: '5', weight_kg: 80.9, logged_at: '2026-01-29' },
  { id: '6', weight_kg: 80.5, logged_at: '2026-02-05' },
  { id: '7', weight_kg: 80.1, logged_at: '2026-02-12' },
  { id: '8', weight_kg: 79.8, logged_at: '2026-02-19' },
  { id: '9', weight_kg: 79.2, logged_at: '2026-02-26' },
  { id: '10', weight_kg: 78.5, logged_at: '2026-03-01' },
];

const chartData = mockWeightData.map((entry) => ({
  date: new Date(entry.logged_at).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
  }),
  weight: entry.weight_kg,
}));

export default function AnalyticsPage() {
  const [newWeight, setNewWeight] = useState('');
  const [logDate, setLogDate] = useState(
    new Date().toISOString().split('T')[0]
  );

  const currentWeight = mockWeightData[mockWeightData.length - 1].weight_kg;
  const startWeight = mockWeightData[0].weight_kg;
  const weightChange = (currentWeight - startWeight).toFixed(1);

  const handleLogWeight = () => {
    if (!newWeight) return;
    // Mock: would send to API
    setNewWeight('');
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
        <TabsList className="w-full sm:w-auto">
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
          <TabsTrigger value="nutrition" className="gap-1.5">
            <UtensilsCrossed className="size-4" />
            Питание
          </TabsTrigger>
        </TabsList>

        {/* Weight tab */}
        <TabsContent value="weight" className="mt-6">
          <div className="flex flex-col gap-6">
            {/* Stats row */}
            <div className="grid gap-4 sm:grid-cols-3">
              <Card className="border-border/50">
                <CardContent className="flex items-center gap-3 pt-6">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-blue-500/10">
                    <Scale className="size-5 text-blue-500" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Текущий вес</p>
                    <p className="text-xl font-bold">{currentWeight} кг</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="border-border/50">
                <CardContent className="flex items-center gap-3 pt-6">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-green-500/10">
                    <TrendingDown className="size-5 text-green-500" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Изменение</p>
                    <p className="text-xl font-bold">{weightChange} кг</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="border-border/50">
                <CardContent className="flex items-center gap-3 pt-6">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-purple-500/10">
                    <CalendarDays className="size-5 text-purple-500" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Записей
                    </p>
                    <p className="text-xl font-bold">{mockWeightData.length}</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Chart */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Динамика веса</CardTitle>
                <CardDescription>
                  Изменение вашего веса за последние 2 месяца
                </CardDescription>
              </CardHeader>
              <CardContent>
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
                        stroke="hsl(var(--primary))"
                        strokeWidth={2}
                        dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

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
                  <Button onClick={handleLogWeight} disabled={!newWeight}>
                    Записать
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Measurements tab */}
        <TabsContent value="measurements" className="mt-6">
          <Card className="border-border/50">
            <CardContent className="flex flex-col items-center justify-center gap-4 py-16">
              <div className="flex size-16 items-center justify-center rounded-full bg-muted">
                <Ruler className="size-8 text-muted-foreground" />
              </div>
              <div className="text-center">
                <Badge variant="secondary" className="mb-3">
                  Скоро
                </Badge>
                <h3 className="text-lg font-semibold">Замеры тела</h3>
                <p className="mt-1 max-w-md text-sm text-muted-foreground">
                  Отслеживайте объёмы груди, талии, бёдер, рук и других частей
                  тела. Эта функция скоро будет доступна.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workouts tab */}
        <TabsContent value="workouts" className="mt-6">
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
                  Начните тренироваться, и здесь появятся графики прогресса, объёма нагрузки и частоты тренировок.
                </p>
              </div>
              <Button variant="outline" asChild>
                <a href="/workouts">Перейти к тренировкам</a>
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Nutrition tab */}
        <TabsContent value="nutrition" className="mt-6">
          <Card className="border-border/50">
            <CardContent className="flex flex-col items-center justify-center gap-4 py-16">
              <div className="flex size-16 items-center justify-center rounded-full bg-muted">
                <UtensilsCrossed className="size-8 text-muted-foreground" />
              </div>
              <div className="text-center">
                <Badge variant="secondary" className="mb-3">
                  Скоро
                </Badge>
                <h3 className="text-lg font-semibold">
                  Аналитика питания
                </h3>
                <p className="mt-1 max-w-md text-sm text-muted-foreground">
                  Графики потребления калорий и макронутриентов за неделю, месяц
                  и произвольный период. Эта функция скоро будет доступна.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
