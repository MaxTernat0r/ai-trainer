'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { userApi } from '@/lib/api/user';
import type { OnboardingData } from '@/types/user';
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Loader2,
  User,
  Target,
  Dumbbell,
  BarChart3,
  Calendar,
  ClipboardCheck,
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const TOTAL_STEPS = 6;

const stepInfo = [
  { title: 'Физические параметры', icon: User },
  { title: 'Цель', icon: Target },
  { title: 'Вид спорта', icon: Dumbbell },
  { title: 'Уровень подготовки', icon: BarChart3 },
  { title: 'График тренировок', icon: Calendar },
  { title: 'Подтверждение', icon: ClipboardCheck },
];

const goals = [
  { value: 'muscle_gain', label: 'Набор мышечной массы' },
  { value: 'fat_loss', label: 'Снижение веса' },
  { value: 'endurance', label: 'Выносливость' },
  { value: 'flexibility', label: 'Гибкость' },
  { value: 'general_fitness', label: 'Общая физическая форма' },
];

const sportTypes = [
  { value: 'gym', label: 'Тренажёрный зал' },
  { value: 'calisthenics', label: 'Калистеника' },
  { value: 'running', label: 'Бег' },
  { value: 'swimming', label: 'Плавание' },
  { value: 'martial_arts', label: 'Единоборства' },
  { value: 'other', label: 'Другое' },
];

const experienceLevels = [
  {
    value: 'beginner',
    label: 'Начинающий',
    description: 'Менее 6 месяцев опыта',
  },
  {
    value: 'intermediate',
    label: 'Средний',
    description: 'От 6 месяцев до 2 лет',
  },
  {
    value: 'advanced',
    label: 'Продвинутый',
    description: 'Более 2 лет опыта',
  },
];

const activityLevels = [
  { value: 'sedentary', label: 'Сидячий образ жизни' },
  { value: 'light', label: 'Лёгкая активность' },
  { value: 'moderate', label: 'Умеренная активность' },
  { value: 'active', label: 'Высокая активность' },
  { value: 'very_active', label: 'Очень высокая активность' },
];

const genders = [
  { value: 'male', label: 'Мужской' },
  { value: 'female', label: 'Женский' },
];

const goalLabels: Record<string, string> = Object.fromEntries(
  goals.map((g) => [g.value, g.label])
);
const sportLabels: Record<string, string> = Object.fromEntries(
  sportTypes.map((s) => [s.value, s.label])
);
const experienceLabels: Record<string, string> = Object.fromEntries(
  experienceLevels.map((e) => [e.value, e.label])
);
const activityLabels: Record<string, string> = Object.fromEntries(
  activityLevels.map((a) => [a.value, a.label])
);
const genderLabels: Record<string, string> = Object.fromEntries(
  genders.map((g) => [g.value, g.label])
);

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const [data, setData] = useState<Partial<OnboardingData>>({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: '',
    height_cm: undefined,
    weight_kg: undefined,
    goal: '',
    sport_type: '',
    experience_level: '',
    activity_level: '',
    training_days_per_week: 3,
    equipment_available: 'full_gym',
    target_weight_kg: null,
    medical_restriction_ids: [],
  });

  const updateField = <K extends keyof OnboardingData>(
    key: K,
    value: OnboardingData[K]
  ) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const canProceed = (): boolean => {
    switch (step) {
      case 0:
        return !!(
          data.first_name &&
          data.date_of_birth &&
          data.gender &&
          data.height_cm &&
          data.weight_kg
        );
      case 1:
        return !!data.goal;
      case 2:
        return !!data.sport_type;
      case 3:
        return !!data.experience_level;
      case 4:
        return !!(data.training_days_per_week && data.activity_level);
      default:
        return true;
    }
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      await userApi.updateProfile(data);
      toast.success('Профиль успешно сохранён');
      router.push('/dashboard');
    } catch {
      toast.error('Ошибка при сохранении профиля');
    } finally {
      setIsLoading(false);
    }
  };

  const next = () => {
    if (step < TOTAL_STEPS - 1) setStep(step + 1);
  };
  const prev = () => {
    if (step > 0) setStep(step - 1);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Progress bar */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Шаг {step + 1} из {TOTAL_STEPS}
          </span>
          <span>{stepInfo[step].title}</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all duration-500"
            style={{ width: `${((step + 1) / TOTAL_STEPS) * 100}%` }}
          />
        </div>
        <div className="flex justify-between">
          {stepInfo.map((s, i) => (
            <div
              key={s.title}
              className={cn(
                'flex size-8 items-center justify-center rounded-full transition-colors',
                i <= step
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground'
              )}
            >
              {i < step ? (
                <Check className="size-4" />
              ) : (
                <s.icon className="size-4" />
              )}
            </div>
          ))}
        </div>
      </div>

      <Card className="border-border/50">
        <CardHeader>
          <CardTitle>{stepInfo[step].title}</CardTitle>
          <CardDescription>
            {step === 0 && 'Расскажите о себе, чтобы мы могли подобрать программу'}
            {step === 1 && 'Какова ваша основная цель тренировок?'}
            {step === 2 && 'Какой вид спорта вам ближе?'}
            {step === 3 && 'Оцените свой уровень подготовки'}
            {step === 4 && 'Как часто вы готовы тренироваться?'}
            {step === 5 && 'Проверьте введённые данные и подтвердите'}
          </CardDescription>
        </CardHeader>

        <CardContent>
          {/* Step 1: Physical params */}
          {step === 0 && (
            <div className="flex flex-col gap-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="first_name">Имя</Label>
                  <Input
                    id="first_name"
                    placeholder="Александр"
                    value={data.first_name || ''}
                    onChange={(e) => updateField('first_name', e.target.value)}
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="last_name">Фамилия</Label>
                  <Input
                    id="last_name"
                    placeholder="Иванов"
                    value={data.last_name || ''}
                    onChange={(e) => updateField('last_name', e.target.value)}
                  />
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="date_of_birth">Дата рождения</Label>
                <Input
                  id="date_of_birth"
                  type="date"
                  value={data.date_of_birth || ''}
                  onChange={(e) => updateField('date_of_birth', e.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label>Пол</Label>
                <div className="grid grid-cols-2 gap-3">
                  {genders.map((g) => (
                    <button
                      key={g.value}
                      type="button"
                      onClick={() => updateField('gender', g.value)}
                      className={cn(
                        'rounded-lg border px-4 py-3 text-sm font-medium transition-colors',
                        data.gender === g.value
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-border hover:border-primary/50 hover:bg-muted'
                      )}
                    >
                      {g.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="height_cm">Рост (см)</Label>
                  <Input
                    id="height_cm"
                    type="number"
                    placeholder="175"
                    value={data.height_cm || ''}
                    onChange={(e) =>
                      updateField('height_cm', Number(e.target.value))
                    }
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="weight_kg">Вес (кг)</Label>
                  <Input
                    id="weight_kg"
                    type="number"
                    placeholder="78"
                    value={data.weight_kg || ''}
                    onChange={(e) =>
                      updateField('weight_kg', Number(e.target.value))
                    }
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Goals */}
          {step === 1 && (
            <div className="grid gap-3 sm:grid-cols-2">
              {goals.map((g) => (
                <button
                  key={g.value}
                  type="button"
                  onClick={() => updateField('goal', g.value)}
                  className={cn(
                    'rounded-lg border px-4 py-4 text-left text-sm font-medium transition-colors',
                    data.goal === g.value
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 hover:bg-muted'
                  )}
                >
                  {g.label}
                </button>
              ))}
            </div>
          )}

          {/* Step 3: Sport type */}
          {step === 2 && (
            <div className="grid gap-3 sm:grid-cols-2">
              {sportTypes.map((s) => (
                <button
                  key={s.value}
                  type="button"
                  onClick={() => updateField('sport_type', s.value)}
                  className={cn(
                    'rounded-lg border px-4 py-4 text-left text-sm font-medium transition-colors',
                    data.sport_type === s.value
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-border hover:border-primary/50 hover:bg-muted'
                  )}
                >
                  {s.label}
                </button>
              ))}
            </div>
          )}

          {/* Step 4: Experience level */}
          {step === 3 && (
            <div className="flex flex-col gap-3">
              {experienceLevels.map((e) => (
                <button
                  key={e.value}
                  type="button"
                  onClick={() => updateField('experience_level', e.value)}
                  className={cn(
                    'rounded-lg border px-4 py-4 text-left transition-colors',
                    data.experience_level === e.value
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50 hover:bg-muted'
                  )}
                >
                  <p
                    className={cn(
                      'text-sm font-medium',
                      data.experience_level === e.value && 'text-primary'
                    )}
                  >
                    {e.label}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {e.description}
                  </p>
                </button>
              ))}
            </div>
          )}

          {/* Step 5: Training schedule */}
          {step === 4 && (
            <div className="flex flex-col gap-6">
              <div className="flex flex-col gap-2">
                <Label>Тренировок в неделю: {data.training_days_per_week}</Label>
                <div className="flex items-center gap-3">
                  {[1, 2, 3, 4, 5, 6, 7].map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => updateField('training_days_per_week', d)}
                      className={cn(
                        'flex size-10 items-center justify-center rounded-full text-sm font-medium transition-colors',
                        data.training_days_per_week === d
                          ? 'bg-primary text-primary-foreground'
                          : 'border border-border hover:border-primary/50 hover:bg-muted'
                      )}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <Label>Уровень активности</Label>
                <div className="flex flex-col gap-2">
                  {activityLevels.map((a) => (
                    <button
                      key={a.value}
                      type="button"
                      onClick={() => updateField('activity_level', a.value)}
                      className={cn(
                        'rounded-lg border px-4 py-3 text-left text-sm font-medium transition-colors',
                        data.activity_level === a.value
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-border hover:border-primary/50 hover:bg-muted'
                      )}
                    >
                      {a.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 6: Summary */}
          {step === 5 && (
            <div className="flex flex-col gap-4">
              <div className="rounded-lg border border-border p-4">
                <div className="grid gap-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Имя</span>
                    <span className="font-medium">
                      {data.first_name} {data.last_name}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Дата рождения</span>
                    <span className="font-medium">{data.date_of_birth}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Пол</span>
                    <span className="font-medium">
                      {genderLabels[data.gender || ''] || '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Рост</span>
                    <span className="font-medium">{data.height_cm} см</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Вес</span>
                    <span className="font-medium">{data.weight_kg} кг</span>
                  </div>
                  <hr className="border-border" />
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Цель</span>
                    <span className="font-medium">
                      {goalLabels[data.goal || ''] || '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Вид спорта</span>
                    <span className="font-medium">
                      {sportLabels[data.sport_type || ''] || '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Уровень</span>
                    <span className="font-medium">
                      {experienceLabels[data.experience_level || ''] || '-'}
                    </span>
                  </div>
                  <hr className="border-border" />
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">
                      Тренировок в неделю
                    </span>
                    <span className="font-medium">
                      {data.training_days_per_week}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Активность</span>
                    <span className="font-medium">
                      {activityLabels[data.activity_level || ''] || '-'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-between gap-3">
          <Button
            variant="outline"
            onClick={prev}
            disabled={step === 0}
          >
            <ArrowLeft className="size-4" />
            Назад
          </Button>
          {step < TOTAL_STEPS - 1 ? (
            <Button onClick={next} disabled={!canProceed()}>
              Далее
              <ArrowRight className="size-4" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={isLoading}>
              {isLoading && <Loader2 className="animate-spin" />}
              Подтвердить
              <Check className="size-4" />
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
