'use client';

import { useState, useMemo } from 'react';
import { Search, Dumbbell, Target, Zap } from 'lucide-react';
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

// --- Mock exercise data ---
interface Exercise {
  id: string;
  name: string;
  name_ru: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  exercise_type: 'compound' | 'isolation' | 'cardio';
  equipment: string | null;
  primary_muscles: string[];
}

const mockExercises: Exercise[] = [
  {
    id: '1',
    name: 'Barbell Bench Press',
    name_ru: 'Жим штанги лёжа',
    difficulty: 'intermediate',
    exercise_type: 'compound',
    equipment: 'Штанга, скамья',
    primary_muscles: ['Грудь', 'Трицепс', 'Передняя дельта'],
  },
  {
    id: '2',
    name: 'Squat',
    name_ru: 'Приседания со штангой',
    difficulty: 'intermediate',
    exercise_type: 'compound',
    equipment: 'Штанга, стойка',
    primary_muscles: ['Квадрицепс', 'Ягодицы', 'Кор'],
  },
  {
    id: '3',
    name: 'Deadlift',
    name_ru: 'Становая тяга',
    difficulty: 'advanced',
    exercise_type: 'compound',
    equipment: 'Штанга',
    primary_muscles: ['Спина', 'Ягодицы', 'Задняя поверхность бедра'],
  },
  {
    id: '4',
    name: 'Pull-ups',
    name_ru: 'Подтягивания',
    difficulty: 'intermediate',
    exercise_type: 'compound',
    equipment: 'Турник',
    primary_muscles: ['Широчайшие', 'Бицепс'],
  },
  {
    id: '5',
    name: 'Overhead Press',
    name_ru: 'Жим штанги стоя',
    difficulty: 'intermediate',
    exercise_type: 'compound',
    equipment: 'Штанга',
    primary_muscles: ['Плечи', 'Трицепс'],
  },
  {
    id: '6',
    name: 'Bicep Curls',
    name_ru: 'Сгибание рук со штангой',
    difficulty: 'beginner',
    exercise_type: 'isolation',
    equipment: 'Штанга / Гантели',
    primary_muscles: ['Бицепс'],
  },
  {
    id: '7',
    name: 'Lateral Raises',
    name_ru: 'Разводка гантелей в стороны',
    difficulty: 'beginner',
    exercise_type: 'isolation',
    equipment: 'Гантели',
    primary_muscles: ['Средняя дельта'],
  },
  {
    id: '8',
    name: 'Triceps Pushdown',
    name_ru: 'Разгибание рук на блоке',
    difficulty: 'beginner',
    exercise_type: 'isolation',
    equipment: 'Блочный тренажёр',
    primary_muscles: ['Трицепс'],
  },
  {
    id: '9',
    name: 'Leg Press',
    name_ru: 'Жим ногами',
    difficulty: 'beginner',
    exercise_type: 'compound',
    equipment: 'Тренажёр',
    primary_muscles: ['Квадрицепс', 'Ягодицы'],
  },
  {
    id: '10',
    name: 'Running',
    name_ru: 'Бег',
    difficulty: 'beginner',
    exercise_type: 'cardio',
    equipment: null,
    primary_muscles: ['Ноги', 'Кардио'],
  },
  {
    id: '11',
    name: 'Plank',
    name_ru: 'Планка',
    difficulty: 'beginner',
    exercise_type: 'isolation',
    equipment: null,
    primary_muscles: ['Кор', 'Пресс'],
  },
  {
    id: '12',
    name: 'Barbell Row',
    name_ru: 'Тяга штанги в наклоне',
    difficulty: 'advanced',
    exercise_type: 'compound',
    equipment: 'Штанга',
    primary_muscles: ['Широчайшие', 'Ромбовидные', 'Бицепс'],
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

const allMuscleGroups = [
  'Все',
  'Грудь',
  'Спина',
  'Плечи',
  'Бицепс',
  'Трицепс',
  'Квадрицепс',
  'Ягодицы',
  'Кор',
  'Широчайшие',
  'Ноги',
];

export default function ExercisesPage() {
  const [search, setSearch] = useState('');
  const [difficulty, setDifficulty] = useState('all');
  const [exerciseType, setExerciseType] = useState('all');
  const [muscleGroup, setMuscleGroup] = useState('Все');

  const filtered = useMemo(() => {
    return mockExercises.filter((ex) => {
      // Search
      if (
        search &&
        !ex.name_ru.toLowerCase().includes(search.toLowerCase()) &&
        !ex.name.toLowerCase().includes(search.toLowerCase())
      ) {
        return false;
      }
      // Difficulty
      if (difficulty !== 'all' && ex.difficulty !== difficulty) {
        return false;
      }
      // Type
      if (exerciseType !== 'all' && ex.exercise_type !== exerciseType) {
        return false;
      }
      // Muscle group
      if (
        muscleGroup !== 'Все' &&
        !ex.primary_muscles.some((m) =>
          m.toLowerCase().includes(muscleGroup.toLowerCase())
        )
      ) {
        return false;
      }
      return true;
    });
  }, [search, difficulty, exerciseType, muscleGroup]);

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

        <Select value={muscleGroup} onValueChange={setMuscleGroup}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Группа мышц" />
          </SelectTrigger>
          <SelectContent>
            {allMuscleGroups.map((group) => (
              <SelectItem key={group} value={group}>
                {group}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {(difficulty !== 'all' || exerciseType !== 'all' || muscleGroup !== 'Все' || search) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setDifficulty('all');
              setExerciseType('all');
              setMuscleGroup('Все');
              setSearch('');
            }}
          >
            Сбросить
          </Button>
        )}
      </div>

      {/* Results count */}
      <p className="text-sm text-muted-foreground">
        Найдено: {filtered.length}{' '}
        {filtered.length === 1
          ? 'упражнение'
          : filtered.length < 5
            ? 'упражнения'
            : 'упражнений'}
      </p>

      {/* Exercise grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((exercise) => (
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
                    className={difficultyColors[exercise.difficulty]}
                  >
                    {difficultyLabels[exercise.difficulty]}
                  </Badge>
                  <Badge
                    variant="outline"
                    className={typeColors[exercise.exercise_type]}
                  >
                    {typeLabels[exercise.exercise_type]}
                  </Badge>
                </div>

                {/* Equipment */}
                {exercise.equipment && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Target className="size-3.5" />
                    <span>{exercise.equipment}</span>
                  </div>
                )}

                {/* Muscle groups */}
                <div className="flex flex-wrap gap-1">
                  {exercise.primary_muscles.map((muscle) => (
                    <Badge
                      key={muscle}
                      variant="secondary"
                      className="text-xs"
                    >
                      {muscle}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* No results */}
      {filtered.length === 0 && (
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
