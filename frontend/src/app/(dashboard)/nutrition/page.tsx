'use client';

import { useState, useRef, useMemo } from 'react';
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
  Loader2,
  X,
  Sparkles,
  Check,
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
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  useDailySummary,
  useNutritionLogs,
  useNutritionPlans,
  useNutritionPlan,
  useLogFood,
  useRecognizeFood,
  useGenerateNutrition,
} from '@/lib/queries/use-nutrition';
import { cn } from '@/lib/utils';
import type { NutritionLog, NutritionPlan, RecognizedFoodItem } from '@/types/nutrition';

// Meal type mapping
const MEAL_TYPES = [
  { value: 'breakfast', label: 'Завтрак' },
  { value: 'lunch', label: 'Обед' },
  { value: 'snack', label: 'Перекус' },
  { value: 'dinner', label: 'Ужин' },
] as const;

function getMealLabel(type: string): string {
  return MEAL_TYPES.find((m) => m.value === type)?.label ?? type;
}

interface MealSection {
  name: string;
  type: string;
  items: NutritionLog[];
  totalCalories: number;
}

function groupLogsByMeal(logs: NutritionLog[]): MealSection[] {
  const groups = new Map<string, NutritionLog[]>();

  for (const log of logs) {
    const existing = groups.get(log.meal_type) ?? [];
    existing.push(log);
    groups.set(log.meal_type, existing);
  }

  // Order by MEAL_TYPES order
  const orderedTypes: string[] = MEAL_TYPES.map((m) => m.value);
  const sections: MealSection[] = [];

  for (const type of orderedTypes) {
    const items = groups.get(type);
    if (items && items.length > 0) {
      sections.push({
        name: getMealLabel(type),
        type,
        items,
        totalCalories: items.reduce((sum, item) => sum + item.calories, 0),
      });
    }
  }

  // Add any meal types not in the predefined list
  for (const [type, items] of groups) {
    if (!orderedTypes.includes(type)) {
      sections.push({
        name: getMealLabel(type),
        type,
        items,
        totalCalories: items.reduce((sum, item) => sum + item.calories, 0),
      });
    }
  }

  return sections;
}

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

function NutrientRingSkeleton() {
  return (
    <div className="flex flex-col items-center gap-2">
      <Skeleton className="size-[100px] rounded-full" />
      <div className="text-center">
        <Skeleton className="mx-auto h-3 w-16" />
        <Skeleton className="mx-auto mt-1 h-3 w-20" />
      </div>
    </div>
  );
}

function MealSectionSkeleton() {
  return (
    <Card className="border-border/50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Skeleton className="size-9 rounded-lg" />
            <Skeleton className="h-5 w-24" />
          </div>
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-3">
          {[1, 2].map((i) => (
            <div key={i}>
              {i > 1 && <Separator className="mb-3" />}
              <div className="flex items-center justify-between">
                <div>
                  <Skeleton className="h-4 w-40" />
                  <Skeleton className="mt-1 h-3 w-52" />
                </div>
                <Skeleton className="h-4 w-16" />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function NutritionPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [foodSheetOpen, setFoodSheetOpen] = useState(false);
  const [foodSheetMealType, setFoodSheetMealType] = useState('breakfast');
  const [generateSheetOpen, setGenerateSheetOpen] = useState(false);
  const [recognitionResult, setRecognitionResult] = useState<RecognizedFoodItem[] | null>(null);
  const [recognitionSheetOpen, setRecognitionSheetOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Food form state
  const [foodName, setFoodName] = useState('');
  const [foodQuantity, setFoodQuantity] = useState('');
  const [foodCalories, setFoodCalories] = useState('');
  const [foodProtein, setFoodProtein] = useState('');
  const [foodFat, setFoodFat] = useState('');
  const [foodCarbs, setFoodCarbs] = useState('');

  // Generate plan form state
  const [genMeals, setGenMeals] = useState('3');

  const dateString = useMemo(() => {
    const y = currentDate.getFullYear();
    const m = String(currentDate.getMonth() + 1).padStart(2, '0');
    const d = String(currentDate.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }, [currentDate]);

  // Queries
  const { data: dailySummary, isLoading: summaryLoading } = useDailySummary(dateString);
  const { data: logs, isLoading: logsLoading } = useNutritionLogs(dateString);
  const { data: plans } = useNutritionPlans();

  // Mutations
  const logFoodMutation = useLogFood();
  const recognizeFoodMutation = useRecognizeFood();
  const generateMutation = useGenerateNutrition();

  // Derive active plan targets
  const activePlan: NutritionPlan | undefined = plans?.find((p) => p.is_active);
  const { data: fullPlan } = useNutritionPlan(activePlan?.id);
  const targets = {
    calories: activePlan?.daily_calories ?? 2500,
    protein: activePlan?.daily_protein_g ?? 180,
    fat: activePlan?.daily_fat_g ?? 80,
    carbs: activePlan?.daily_carbs_g ?? 280,
  };

  // Group logs into meal sections
  const mealSections = useMemo(() => {
    if (!logs) return [];
    return groupLogsByMeal(logs);
  }, [logs]);

  const summary = dailySummary ?? {
    total_calories: 0,
    total_protein_g: 0,
    total_fat_g: 0,
    total_carbs_g: 0,
    meals_logged: 0,
  };

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

  const resetFoodForm = () => {
    setFoodName('');
    setFoodQuantity('');
    setFoodCalories('');
    setFoodProtein('');
    setFoodFat('');
    setFoodCarbs('');
  };

  const openFoodSheet = (mealType: string) => {
    setFoodSheetMealType(mealType);
    resetFoodForm();
    setFoodSheetOpen(true);
  };

  const handleLogFood = () => {
    if (!foodName || !foodCalories) return;

    logFoodMutation.mutate(
      {
        food_name: foodName,
        meal_type: foodSheetMealType,
        quantity_g: Number(foodQuantity) || 100,
        calories: Number(foodCalories),
        protein_g: Number(foodProtein) || 0,
        fat_g: Number(foodFat) || 0,
        carbs_g: Number(foodCarbs) || 0,
        logged_at: new Date(currentDate).toISOString(),
        date: dateString,
      },
      {
        onSuccess: () => {
          toast.success('Продукт записан');
          setFoodSheetOpen(false);
          resetFoodForm();
        },
        onError: () => {
          toast.error('Не удалось записать продукт');
        },
      }
    );
  };

  const handlePhotoRecognize = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    recognizeFoodMutation.mutate(file, {
      onSuccess: (result) => {
        if (result.is_food && result.items.length > 0) {
          setRecognitionResult(result.items);
          setRecognitionSheetOpen(true);
        } else {
          toast.error('Не удалось распознать еду на фото');
        }
      },
      onError: () => {
        toast.error('Ошибка распознавания фото');
      },
    });

    // Reset file input
    e.target.value = '';
  };

  const handleAddRecognizedItem = (item: RecognizedFoodItem) => {
    logFoodMutation.mutate(
      {
        food_name: item.food_name,
        meal_type: 'snack',
        quantity_g: item.portion_grams,
        calories: item.calories,
        protein_g: item.protein_g,
        fat_g: item.fat_g,
        carbs_g: item.carbs_g,
        date: dateString,
      },
      {
        onSuccess: () => {
          toast.success(`${item.food_name} добавлен`);
        },
        onError: () => {
          toast.error('Не удалось добавить продукт');
        },
      }
    );
  };

  const handleGeneratePlan = () => {
    generateMutation.mutate(
      {
        meals_per_day: Number(genMeals) || 3,
      },
      {
        onSuccess: () => {
          toast.success('План питания сгенерирован!');
          setGenerateSheetOpen(false);
        },
        onError: () => {
          toast.error('Не удалось сгенерировать план');
        },
      }
    );
  };

  const isLoading = summaryLoading || logsLoading;

  // Build the list of all meal types for "Add food" buttons (show all even if empty)
  const allMealSections = useMemo(() => {
    if (isLoading) return [];
    const existing = new Set(mealSections.map((s) => s.type));
    const result = [...mealSections];
    for (const mt of MEAL_TYPES) {
      if (!existing.has(mt.value)) {
        result.push({
          name: mt.label,
          type: mt.value,
          items: [],
          totalCalories: 0,
        });
      }
    }
    // Sort by MEAL_TYPES order
    const order: string[] = MEAL_TYPES.map((m) => m.value);
    result.sort((a, b) => {
      const ia = order.indexOf(a.type);
      const ib = order.indexOf(b.type);
      return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
    });
    return result;
  }, [mealSections, isLoading]);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Питание</h1>
          <p className="text-muted-foreground">
            Отслеживайте калории и макронутриенты
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="gap-1.5"
          onClick={() => setGenerateSheetOpen(true)}
        >
          <Sparkles className="size-4" />
          Создать план
        </Button>
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

      {/* Active plan badge */}
      {activePlan && (
        <div className="flex items-center justify-center">
          <Badge variant="secondary" className="gap-1.5">
            <Sparkles className="size-3" />
            План: {activePlan.title} ({activePlan.daily_calories} ккал)
          </Badge>
        </div>
      )}

      {/* Plan meals display */}
      {fullPlan && fullPlan.meals && fullPlan.meals.length > 0 ? (
        <div className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold">Мой план</h2>
          {fullPlan.meals.map((meal) => {
            const mealCalories = meal.items?.reduce((sum, item) => {
              return sum + Math.round((item.food_item.calories_per_100g * item.quantity_g) / 100);
            }, 0) ?? 0;
            return (
            <Card key={meal.id} className="border-border/50">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex size-9 items-center justify-center rounded-lg bg-green-500/10">
                      <UtensilsCrossed className="size-4 text-green-600" />
                    </div>
                    <CardTitle className="text-base">{meal.name}</CardTitle>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {mealCalories} ккал
                  </Badge>
                </div>
              </CardHeader>
              {meal.items && meal.items.length > 0 && (
                <CardContent className="pt-0">
                  <div className="flex flex-col gap-2">
                    {meal.items.map((item, idx) => {
                      const qty = item.quantity_g;
                      const food = item.food_item;
                      const cal = Math.round((food.calories_per_100g * qty) / 100);
                      const prot = Math.round((food.protein_per_100g * qty) / 100);
                      const fat = Math.round((food.fat_per_100g * qty) / 100);
                      const carbs = Math.round((food.carbs_per_100g * qty) / 100);
                      return (
                        <div key={item.id}>
                          {idx > 0 && <Separator className="mb-2" />}
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm font-medium">{food.name_ru || food.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {qty} г | Б {prot}г | Ж {fat}г | У {carbs}г
                              </p>
                            </div>
                            <span className="text-sm font-medium text-muted-foreground">
                              {cal} ккал
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              )}
            </Card>
            );
          })}
        </div>
      ) : !activePlan && !summaryLoading ? (
        <Card className="border-dashed border-border">
          <CardContent className="flex flex-col items-center gap-3 py-8">
            <Sparkles className="size-8 text-muted-foreground" />
            <div className="text-center">
              <p className="font-medium">Нет плана питания</p>
              <p className="text-sm text-muted-foreground">
                Создайте персональный план на основе ваших параметров
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5"
              onClick={() => setGenerateSheetOpen(true)}
            >
              <Sparkles className="size-4" />
              Создать план
            </Button>
          </CardContent>
        </Card>
      ) : null}

      {/* KBZHU Ring Charts */}
      <Card className="border-border/50">
        <CardContent className="pt-6">
          {summaryLoading ? (
            <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
              <NutrientRingSkeleton />
              <NutrientRingSkeleton />
              <NutrientRingSkeleton />
              <NutrientRingSkeleton />
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
              <NutrientRing
                label="Калории"
                current={summary.total_calories}
                target={targets.calories}
                unit="ккал"
                color="#f97316"
                iconColorClass="text-orange-500"
                icon={Flame}
              />
              <NutrientRing
                label="Белки"
                current={summary.total_protein_g}
                target={targets.protein}
                unit="г"
                color="#ef4444"
                iconColorClass="text-red-500"
                icon={Beef}
              />
              <NutrientRing
                label="Жиры"
                current={summary.total_fat_g}
                target={targets.fat}
                unit="г"
                color="#3b82f6"
                iconColorClass="text-blue-500"
                icon={Droplets}
              />
              <NutrientRing
                label="Углеводы"
                current={summary.total_carbs_g}
                target={targets.carbs}
                unit="г"
                color="#eab308"
                iconColorClass="text-yellow-500"
                icon={Wheat}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Meal sections */}
      <div className="flex flex-col gap-4">
        {logsLoading ? (
          <>
            <MealSectionSkeleton />
            <MealSectionSkeleton />
            <MealSectionSkeleton />
          </>
        ) : (
          allMealSections.map((meal) => (
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
                {meal.items.length > 0 && (
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
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  className="mt-4 w-full"
                  onClick={() => openFoodSheet(meal.type)}
                >
                  <Plus className="size-3.5" />
                  Добавить продукт
                </Button>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Daily summary */}
      <Card className="border-border/50">
        <CardHeader>
          <CardTitle className="text-base">Итого за день</CardTitle>
        </CardHeader>
        <CardContent>
          {summaryLoading ? (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-20 rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="rounded-lg bg-orange-500/10 p-3 text-center">
                <p className="text-lg font-bold text-orange-600 dark:text-orange-400">
                  {summary.total_calories}
                </p>
                <p className="text-xs text-muted-foreground">
                  / {targets.calories} ккал
                </p>
              </div>
              <div className="rounded-lg bg-red-500/10 p-3 text-center">
                <p className="text-lg font-bold text-red-600 dark:text-red-400">
                  {summary.total_protein_g}г
                </p>
                <p className="text-xs text-muted-foreground">
                  / {targets.protein}г белка
                </p>
              </div>
              <div className="rounded-lg bg-blue-500/10 p-3 text-center">
                <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                  {summary.total_fat_g}г
                </p>
                <p className="text-xs text-muted-foreground">
                  / {targets.fat}г жиров
                </p>
              </div>
              <div className="rounded-lg bg-yellow-500/10 p-3 text-center">
                <p className="text-lg font-bold text-yellow-600 dark:text-yellow-400">
                  {summary.total_carbs_g}г
                </p>
                <p className="text-xs text-muted-foreground">
                  / {targets.carbs}г углеводов
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Hidden file input for photo recognition */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleFileSelected}
      />

      {/* Floating "scan by photo" button */}
      <div className="fixed bottom-24 right-6 z-40 md:bottom-8">
        <Button
          size="lg"
          className="size-14 rounded-full shadow-lg"
          onClick={handlePhotoRecognize}
          disabled={recognizeFoodMutation.isPending}
        >
          {recognizeFoodMutation.isPending ? (
            <Loader2 className="size-6 animate-spin" />
          ) : (
            <Camera className="size-6" />
          )}
          <span className="sr-only">Распознать по фото</span>
        </Button>
      </div>

      {/* Food logging sheet */}
      <Sheet open={foodSheetOpen} onOpenChange={setFoodSheetOpen}>
        <SheetContent side="bottom" className="max-h-[85vh] overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Добавить продукт</SheetTitle>
            <SheetDescription>
              {getMealLabel(foodSheetMealType)}
            </SheetDescription>
          </SheetHeader>
          <div className="flex flex-col gap-4 p-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="food-name">Название</Label>
              <Input
                id="food-name"
                placeholder="Куриная грудка"
                value={foodName}
                onChange={(e) => setFoodName(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="food-quantity">Вес (г)</Label>
                <Input
                  id="food-quantity"
                  type="number"
                  placeholder="100"
                  value={foodQuantity}
                  onChange={(e) => setFoodQuantity(e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="food-calories">Калории</Label>
                <Input
                  id="food-calories"
                  type="number"
                  placeholder="165"
                  value={foodCalories}
                  onChange={(e) => setFoodCalories(e.target.value)}
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="flex flex-col gap-2">
                <Label htmlFor="food-protein">Белки (г)</Label>
                <Input
                  id="food-protein"
                  type="number"
                  step="0.1"
                  placeholder="31"
                  value={foodProtein}
                  onChange={(e) => setFoodProtein(e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="food-fat">Жиры (г)</Label>
                <Input
                  id="food-fat"
                  type="number"
                  step="0.1"
                  placeholder="3.6"
                  value={foodFat}
                  onChange={(e) => setFoodFat(e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="food-carbs">Углеводы (г)</Label>
                <Input
                  id="food-carbs"
                  type="number"
                  step="0.1"
                  placeholder="0"
                  value={foodCarbs}
                  onChange={(e) => setFoodCarbs(e.target.value)}
                />
              </div>
            </div>
            <Button
              className="mt-2"
              onClick={handleLogFood}
              disabled={!foodName || !foodCalories || logFoodMutation.isPending}
            >
              {logFoodMutation.isPending ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Plus className="size-4" />
              )}
              Добавить
            </Button>
          </div>
        </SheetContent>
      </Sheet>

      {/* Recognition results sheet */}
      <Sheet open={recognitionSheetOpen} onOpenChange={setRecognitionSheetOpen}>
        <SheetContent side="bottom" className="max-h-[85vh] overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Распознанные продукты</SheetTitle>
            <SheetDescription>
              Нажмите на продукт, чтобы добавить его в журнал
            </SheetDescription>
          </SheetHeader>
          <div className="flex flex-col gap-3 p-4">
            {recognitionResult?.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between rounded-lg border border-border p-3"
              >
                <div>
                  <p className="text-sm font-medium">{item.food_name}</p>
                  <p className="text-xs text-muted-foreground">
                    {item.portion_grams}г | {item.calories} ккал | Б {item.protein_g}г | Ж {item.fat_g}г | У {item.carbs_g}г
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Точность: {Math.round(item.confidence_score * 100)}%
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleAddRecognizedItem(item)}
                  disabled={logFoodMutation.isPending}
                >
                  <Check className="size-4" />
                </Button>
              </div>
            ))}
          </div>
        </SheetContent>
      </Sheet>

      {/* Generate plan sheet */}
      <Sheet open={generateSheetOpen} onOpenChange={setGenerateSheetOpen}>
        <SheetContent side="bottom" className="max-h-[85vh] overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Сгенерировать план питания</SheetTitle>
            <SheetDescription>
              ИИ создаст персональный план на основе ваших параметров
            </SheetDescription>
          </SheetHeader>
          <div className="flex flex-col gap-4 p-4">
            <div className="rounded-lg border border-dashed border-border p-4">
              <div className="flex items-start gap-3">
                <Sparkles className="mt-0.5 size-5 text-primary" />
                <div className="flex flex-col gap-1">
                  <p className="text-sm font-medium">Калории и БЖУ рассчитаются автоматически</p>
                  <p className="text-xs text-muted-foreground">
                    На основе вашего веса, роста, возраста, уровня активности и цели из профиля.
                    Аллергии и нелюбимые продукты будут учтены.
                  </p>
                </div>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="gen-meals">Приёмов пищи в день</Label>
              <div className="flex items-center gap-3">
                {[2, 3, 4, 5, 6].map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => setGenMeals(String(n))}
                    className={cn(
                      'flex size-10 items-center justify-center rounded-full text-sm font-medium transition-colors',
                      Number(genMeals) === n
                        ? 'bg-primary text-primary-foreground'
                        : 'border border-border hover:border-primary/50 hover:bg-muted'
                    )}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
            <Button
              className="mt-2"
              onClick={handleGeneratePlan}
              disabled={generateMutation.isPending}
            >
              {generateMutation.isPending ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Sparkles className="size-4" />
              )}
              Сгенерировать
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
