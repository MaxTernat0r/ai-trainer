'use client';

import { useState, useMemo } from 'react';
import { Search, Dumbbell, Target } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { useExercises, useMuscleGroups, useEquipment } from '@/lib/queries/use-exercises';

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

const typeLabels: Record<string, string> = {
  compound: 'Базовое',
  isolation: 'Изолирующее',
  cardio: 'Кардио',
};

const typeColors: Record<string, string> = {
  compound: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
  isolation: 'bg-purple-500/10 text-purple-600 dark:text-purple-400',
  cardio: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
};

export default function ExercisesPage() {
  const [search, setSearch] = useState('');
  const [difficulty, setDifficulty] = useState('all');
  const [exerciseType, setExerciseType] = useState('all');
  const [muscleGroupId, setMuscleGroupId] = useState('all');
  const [equipmentId, setEquipmentId] = useState('all');

  // Build filters for the API query
  const filters = useMemo(() => {
    const f: Record<string, string> = {};
    if (search.trim()) f.search = search.trim();
    if (difficulty !== 'all') f.difficulty = difficulty;
    if (exerciseType !== 'all') f.exercise_type = exerciseType;
    if (muscleGroupId !== 'all') f.muscle_group_id = muscleGroupId;
    if (equipmentId !== 'all') f.equipment_id = equipmentId;
    return f;
  }, [search, difficulty, exerciseType, muscleGroupId, equipmentId]);

  const { data: exercises, isLoading: exercisesLoading } = useExercises(filters);
  const { data: muscleGroups } = useMuscleGroups();
  const { data: equipmentList } = useEquipment();

  const hasActiveFilters =
    difficulty !== 'all' ||
    exerciseType !== 'all' ||
    muscleGroupId !== 'all' ||
    equipmentId !== 'all' ||
    search.trim().length > 0;

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Библиотека упражнений
        </h1>
        <p className="text-muted-foreground">
          Изучайте упражнения и добавляйте их в свои тренировки
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Поиск упражнений..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <Select value={difficulty} onValueChange={setDifficulty}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Сложность" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Все уровни</SelectItem>
            <SelectItem value="beginner">Начинающий</SelectItem>
            <SelectItem value="intermediate">Средний</SelectItem>
            <SelectItem value="advanced">Продвинутый</SelectItem>
          </SelectContent>
        </Select>

        <Select value={exerciseType} onValueChange={setExerciseType}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Тип" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Все типы</SelectItem>
            <SelectItem value="compound">Базовое</SelectItem>
            <SelectItem value="isolation">Изолирующее</SelectItem>
            <SelectItem value="cardio">Кардио</SelectItem>
          </SelectContent>
        </Select>

        <Select value={muscleGroupId} onValueChange={setMuscleGroupId}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Группа мышц" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Все мышцы</SelectItem>
            {muscleGroups?.map((group) => (
              <SelectItem key={group.id} value={group.id}>
                {group.name_ru}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={equipmentId} onValueChange={setEquipmentId}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Оборудование" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Любое оборудование</SelectItem>
            {equipmentList?.map((eq) => (
              <SelectItem key={eq.id} value={eq.id}>
                {eq.name_ru}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setDifficulty('all');
              setExerciseType('all');
              setMuscleGroupId('all');
              setEquipmentId('all');
              setSearch('');
            }}
          >
            Сбросить
          </Button>
        )}
      </div>

      {/* Results count */}
      {!exercisesLoading && exercises && (
        <p className="text-sm text-muted-foreground">
          Найдено: {exercises.length}{' '}
          {exercises.length === 1
            ? 'упражнение'
            : exercises.length < 5
              ? 'упражнения'
              : 'упражнений'}
        </p>
      )}

      {/* Loading skeleton */}
      {exercisesLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="border-border/50">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <Skeleton className="h-5 w-3/4" />
                  <Skeleton className="size-8 rounded-lg" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3">
                  <div className="flex gap-1.5">
                    <Skeleton className="h-5 w-20 rounded-full" />
                    <Skeleton className="h-5 w-20 rounded-full" />
                  </div>
                  <Skeleton className="h-4 w-2/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Exercise grid */}
      {!exercisesLoading && exercises && exercises.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {exercises.map((exercise) => (
            <Card
              key={exercise.id}
              className="border-border/50 transition-colors hover:border-primary/20 hover:shadow-md"
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base">
                    {exercise.name_ru}
                  </CardTitle>
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                    <Dumbbell className="size-4 text-muted-foreground" />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-3">
                  {/* Badges row */}
                  <div className="flex flex-wrap gap-1.5">
                    <Badge
                      variant="outline"
                      className={difficultyColors[exercise.difficulty] ?? ''}
                    >
                      {difficultyLabels[exercise.difficulty] ?? exercise.difficulty}
                    </Badge>
                    <Badge
                      variant="outline"
                      className={typeColors[exercise.exercise_type] ?? ''}
                    >
                      {typeLabels[exercise.exercise_type] ?? exercise.exercise_type}
                    </Badge>
                  </div>

                  {/* Equipment */}
                  {exercise.equipment && (
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Target className="size-3.5" />
                      <span>{exercise.equipment.name_ru}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* No results */}
      {!exercisesLoading && exercises && exercises.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-4 py-12">
          <div className="flex size-16 items-center justify-center rounded-full bg-muted">
            <Search className="size-8 text-muted-foreground" />
          </div>
          <div className="text-center">
            <h3 className="text-lg font-semibold">Ничего не найдено</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Попробуйте изменить параметры поиска или фильтры
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
