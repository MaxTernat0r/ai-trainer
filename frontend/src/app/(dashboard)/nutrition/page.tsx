'use client';

import { useState } from 'react';
import {
  Plus,
  Camera,
  ChevronLeft,
  ChevronRight,
  Flame,
  Beef,
  Droplets,
  Wheat,
  UtensilsCrossed,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import type { NutritionLog, DailySummary } from '@/types/nutrition';

// --- Mock data ---
const mockDailySummary: DailySummary = {
  date: '2026-03-01',
  total_calories: 1850,
  total_protein_g: 142,
  total_fat_g: 58,
  total_carbs_g: 195,
  meals_logged: 3,
};

const targets = {
  calories: 2500,
  protein: 180,
  fat: 80,
  carbs: 280,
};

interface MealSection {
  name: string;
  type: string;
  items: NutritionLog[];
  totalCalories: number;
}

const mockMeals: MealSection[] = [
  {
    name: 'Завтрак',
    type: 'breakfast',
    totalCalories: 620,
    items: [
      { id: '1', food_name: 'Овсянка с бананом', meal_type: 'breakfast', quantity_g: 300, calories: 350, protein_g: 12, fat_g: 8, carbs_g: 55, photo_url: null, logged_at: '2026-03-01T08:00:00Z', notes: null },
      { id: '2', food_name: 'Яйца варёные (2 шт.)', meal_type: 'breakfast', quantity_g: 120, calories: 170, protein_g: 14, fat_g: 11, carbs_g: 1, photo_url: null, logged_at: '2026-03-01T08:00:00Z', notes: null },
      { id: '3', food_name: 'Кофе с молоком', meal_type: 'breakfast', quantity_g: 250, calories: 100, protein_g: 5, fat_g: 4, carbs_g: 10, photo_url: null, logged_at: '2026-03-01T08:15:00Z', notes: null },
    ],
  },
  {
    name: 'Обед',
    type: 'lunch',
    totalCalories: 750,
    items: [
      { id: '4', food_name: 'Куриная грудка гриль', meal_type: 'lunch', quantity_g: 200, calories: 330, protein_g: 62, fat_g: 7, carbs_g: 0, photo_url: null, logged_at: '2026-03-01T13:00:00Z', notes: null },
      { id: '5', food_name: 'Бурый рис', meal_type: 'lunch', quantity_g: 150, calories: 170, protein_g: 4, fat_g: 1, carbs_g: 36, photo_url: null, logged_at: '2026-03-01T13:00:00Z', notes: null },
      { id: '6', food_name: 'Овощной салат', meal_type: 'lunch', quantity_g: 200, calories: 80, protein_g: 3, fat_g: 4, carbs_g: 8, photo_url: null, logged_at: '2026-03-01T13:00:00Z', notes: null },
      { id: '7', food_name: 'Компот', meal_type: 'lunch', quantity_g: 250, calories: 170, protein_g: 0, fat_g: 0, carbs_g: 42, photo_url: null, logged_at: '2026-03-01T13:00:00Z', notes: null },
    ],
  },
  {
    name: 'Перекус',
    type: 'snack',
    totalCalories: 280,
    items: [
      { id: '8', food_name: 'Протеиновый батончик', meal_type: 'snack', quantity_g: 60, calories: 200, protein_g: 20, fat_g: 8, carbs_g: 18, photo_url: null, logged_at: '2026-03-01T16:00:00Z', notes: null },
      { id: '9', food_name: 'Яблоко', meal_type: 'snack', quantity_g: 180, calories: 80, protein_g: 0.5, fat_g: 0, carbs_g: 19, photo_url: null, logged_at: '2026-03-01T16:00:00Z', notes: null },
    ],
  },
  {
    name: 'Ужин',
    type: 'dinner',
    totalCalories: 200,
    items: [
      { id: '10', food_name: 'Творог 5%', meal_type: 'dinner', quantity_g: 200, calories: 200, protein_g: 22, fat_g: 10, carbs_g: 6, photo_url: null, logged_at: '2026-03-01T19:00:00Z', notes: null },
    ],
  },
];

// Circular progress ring
function NutrientRing({
  label,
  current,
  target,
  unit,
  color,
  iconColorClass,
  icon: Icon,
}: {
  label: string;
  current: number;
  target: number;
  unit: string;
  color: string;
  iconColorClass: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  const percentage = Math.min((current / target) * 100, 100);
  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative">
        <svg width="100" height="100" viewBox="0 0 100 100" className="-rotate-90">
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-muted/30"
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-700"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Icon className={`size-4 mb-0.5 ${iconColorClass}`} />
          <span className="text-sm font-bold">{current}</span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-xs font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">
          из {target} {unit}
        </p>
      </div>
    </div>
  );
}

export default function NutritionPage() {
  const [currentDate, setCurrentDate] = useState(new Date());

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('ru-RU', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
    });
  };

  const prevDay = () => {
    setCurrentDate((prev) => {
      const d = new Date(prev);
      d.setDate(d.getDate() - 1);
      return d;
    });
  };

  const nextDay = () => {
    setCurrentDate((prev) => {
      const d = new Date(prev);
      d.setDate(d.getDate() + 1);
      return d;
    });
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Питание</h1>
        <p className="text-muted-foreground">
          Отслеживайте калории и макронутриенты
        </p>
      </div>

      {/* Date selector */}
      <div className="flex items-center justify-center gap-4">
        <Button variant="ghost" size="icon" onClick={prevDay}>
          <ChevronLeft className="size-5" />
        </Button>
        <p className="min-w-48 text-center font-medium capitalize">
          {formatDate(currentDate)}
        </p>
        <Button variant="ghost" size="icon" onClick={nextDay}>
          <ChevronRight className="size-5" />
        </Button>
      </div>

      {/* KBZHU Ring Charts */}
      <Card className="border-border/50">
        <CardContent className="pt-6">
          <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
            <NutrientRing
              label="Калории"
              current={mockDailySummary.total_calories}
              target={targets.calories}
              unit="ккал"
              color="#f97316"
              iconColorClass="text-orange-500"
              icon={Flame}
            />
            <NutrientRing
              label="Белки"
              current={mockDailySummary.total_protein_g}
              target={targets.protein}
              unit="г"
              color="#ef4444"
              iconColorClass="text-red-500"
              icon={Beef}
            />
            <NutrientRing
              label="Жиры"
              current={mockDailySummary.total_fat_g}
              target={targets.fat}
              unit="г"
              color="#3b82f6"
              iconColorClass="text-blue-500"
              icon={Droplets}
            />
            <NutrientRing
              label="Углеводы"
              current={mockDailySummary.total_carbs_g}
              target={targets.carbs}
              unit="г"
              color="#eab308"
              iconColorClass="text-yellow-500"
              icon={Wheat}
            />
          </div>
        </CardContent>
      </Card>

      {/* Meal sections */}
      <div className="flex flex-col gap-4">
        {mockMeals.map((meal) => (
          <Card key={meal.type} className="border-border/50">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10">
                    <UtensilsCrossed className="size-4 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-base">{meal.name}</CardTitle>
                  </div>
                </div>
                <Badge variant="secondary" className="text-sm">
                  {meal.totalCalories} ккал
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                {meal.items.map((item, idx) => (
                  <div key={item.id}>
                    {idx > 0 && <Separator className="mb-3" />}
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">{item.food_name}</p>
                        <p className="text-xs text-muted-foreground">
                          {item.quantity_g} г | Б {item.protein_g}г | Ж {item.fat_g}г | У {item.carbs_g}г
                        </p>
                      </div>
                      <span className="text-sm font-medium text-muted-foreground">
                        {item.calories} ккал
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <Button variant="ghost" size="sm" className="mt-4 w-full">
                <Plus className="size-3.5" />
                Добавить продукт
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Daily summary */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="text-base">Итого за день</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-lg bg-orange-500/10 p-3 text-center">
              <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                {mockDailySummary.total_calories}
              </p>
              <p className="text-xs text-muted-foreground">
                / {targets.calories} ккал
              </p>
            </div>
            <div className="rounded-lg bg-red-500/10 p-3 text-center">
              <p className="text-lg font-bold text-red-600 dark:text-red-400">
                {mockDailySummary.total_protein_g}г
              </p>
              <p className="text-xs text-muted-foreground">
                / {targets.protein}г белка
              </p>
            </div>
            <div className="rounded-lg bg-blue-500/10 p-3 text-center">
              <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                {mockDailySummary.total_fat_g}г
              </p>
              <p className="text-xs text-muted-foreground">
                / {targets.fat}г жиров
              </p>
            </div>
            <div className="rounded-lg bg-yellow-500/10 p-3 text-center">
              <p className="text-lg font-bold text-yellow-600 dark:text-yellow-400">
                {mockDailySummary.total_carbs_g}г
              </p>
              <p className="text-xs text-muted-foreground">
                / {targets.carbs}г углеводов
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Floating "scan by photo" button */}
      <div className="fixed bottom-24 right-6 z-40 md:bottom-8">
        <Button size="lg" className="size-14 rounded-full shadow-lg">
          <Camera className="size-6" />
          <span className="sr-only">Распознать по фото</span>
        </Button>
      </div>
    </div>
  );
}
