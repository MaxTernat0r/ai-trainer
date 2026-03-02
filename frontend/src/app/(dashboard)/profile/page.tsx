'use client';

import { useState } from 'react';
import {
  User as UserIcon,
  Mail,
  CalendarDays,
  Ruler,
  Scale,
  Target,
  Dumbbell,
  Shield,
  LogOut,
  Pencil,
  Heart,
  Activity,
  Trophy,
  Loader2,
  UtensilsCrossed,
  AlertTriangle,
  ThumbsDown,
  NotebookPen,
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
import { Skeleton } from '@/components/ui/skeleton';
import { useProfile } from '@/lib/queries/use-profile';
import { useAuthStore } from '@/lib/stores/auth-store';
import { authApi } from '@/lib/api/auth';
import { toast } from 'sonner';
import type { MedicalRestriction } from '@/types/user';

const genderLabels: Record<string, string> = {
  male: 'Мужской',
  female: 'Женский',
  other: 'Другое',
};

const experienceLabels: Record<string, string> = {
  beginner: 'Начинающий',
  intermediate: 'Средний',
  advanced: 'Продвинутый',
  expert: 'Эксперт',
};

const goalLabels: Record<string, string> = {
  muscle_gain: 'Набор массы',
  fat_loss: 'Жиросжигание',
  strength: 'Увеличение силы',
  endurance: 'Выносливость',
  health: 'Здоровье',
  recomp: 'Рекомпозиция',
  general_fitness: 'Общая физическая форма',
  flexibility: 'Гибкость',
};

const sportLabels: Record<string, string> = {
  bodybuilding: 'Бодибилдинг',
  powerlifting: 'Пауэрлифтинг',
  crossfit: 'Кроссфит',
  calisthenics: 'Калистеника',
  general: 'Общая физ. подготовка',
  gym: 'Тренажёрный зал',
  running: 'Бег',
  swimming: 'Плавание',
  martial_arts: 'Единоборства',
  other: 'Другое',
};

const activityLabels: Record<string, string> = {
  sedentary: 'Малоподвижный',
  light: 'Лёгкая активность',
  moderate: 'Умеренная активность',
  active: 'Высокая активность',
  very_active: 'Очень высокая',
};

function InfoRow({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number | null;
}) {
  return (
    <div className="flex items-center justify-between py-2.5">
      <div className="flex items-center gap-2.5 text-muted-foreground">
        <Icon className="size-4" />
        <span className="text-sm">{label}</span>
      </div>
      <span className="text-sm font-medium">{value ?? '\u2014'}</span>
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      {/* Header skeleton */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Skeleton className="h-8 w-32" />
          <Skeleton className="mt-2 h-5 w-64" />
        </div>
        <Skeleton className="h-10 w-48" />
      </div>

      {/* Avatar skeleton */}
      <div className="flex items-center gap-4">
        <Skeleton className="size-20 rounded-full" />
        <div className="flex flex-col gap-2">
          <Skeleton className="h-6 w-40" />
          <Skeleton className="h-4 w-48" />
          <Skeleton className="mt-1 h-5 w-28" />
        </div>
      </div>

      {/* Cards skeleton */}
      {Array.from({ length: 4 }).map((_, i) => (
        <Card key={i} className="border-border/50">
          <CardHeader>
            <Skeleton className="h-6 w-48" />
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-3">
              {Array.from({ length: 3 }).map((__, j) => (
                <div key={j} className="flex items-center justify-between">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-24" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default function ProfilePage() {
  const { data: profile, isLoading, isError } = useProfile();
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await authApi.logout();
    } catch {
      // Even if logout API fails, clear local state
    } finally {
      clearAuth();
      window.location.href = '/login';
    }
  };

  if (isLoading) {
    return <ProfileSkeleton />;
  }

  if (isError || !profile) {
    return (
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Профиль</h1>
          <p className="text-muted-foreground">
            Управляйте персональными данными и настройками
          </p>
        </div>
        <Card className="border-destructive/30">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">
              Не удалось загрузить данные профиля. Попробуйте обновить страницу.
            </p>
          </CardContent>
        </Card>

        <Separator />
        <Card className="border-destructive/30">
          <CardContent className="flex flex-col gap-4 pt-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="font-medium">Выйти из аккаунта</p>
              <p className="text-sm text-muted-foreground">
                Вы будете перенаправлены на страницу входа
              </p>
            </div>
            <Button
              variant="destructive"
              onClick={handleLogout}
              disabled={isLoggingOut}
            >
              {isLoggingOut ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <LogOut className="size-4" />
              )}
              Выйти из аккаунта
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const fullName =
    [profile.first_name, profile.last_name].filter(Boolean).join(' ') ||
    'Не указано';

  const age = profile.date_of_birth
    ? Math.floor(
        (Date.now() - new Date(profile.date_of_birth).getTime()) /
          (365.25 * 24 * 60 * 60 * 1000)
      )
    : null;

  const email = user?.email ?? '\u2014';
  const isVerified = user?.is_verified ?? false;
  const avatarUrl = user?.avatar_url ?? null;

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Профиль</h1>
          <p className="text-muted-foreground">
            Управляйте персональными данными и настройками
          </p>
        </div>
        <Button variant="outline">
          <Pencil className="size-4" />
          Редактировать профиль
        </Button>
      </div>

      {/* Avatar and name */}
      <div className="flex items-center gap-4">
        <div className="flex size-20 items-center justify-center rounded-full bg-primary/10 ring-4 ring-background">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt="Avatar"
              className="size-full rounded-full object-cover"
            />
          ) : (
            <UserIcon className="size-10 text-primary" />
          )}
        </div>
        <div>
          <h2 className="text-xl font-bold">{fullName}</h2>
          <p className="text-sm text-muted-foreground">{email}</p>
          <div className="mt-1 flex items-center gap-2">
            {isVerified && (
              <Badge variant="secondary" className="gap-1 text-xs">
                <Shield className="size-3" />
                Верифицирован
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Profile info card */}
      <Card className="border-border/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <UserIcon className="size-5 text-primary" />
            <CardTitle>Личная информация</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-border/50">
            <InfoRow icon={UserIcon} label="Имя" value={fullName} />
            <InfoRow icon={Mail} label="Email" value={email} />
          </div>
        </CardContent>
      </Card>

      {/* Physical params card */}
      <Card className="border-border/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="size-5 text-blue-500" />
            <CardTitle>Физические параметры</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-border/50">
            <InfoRow
              icon={UserIcon}
              label="Пол"
              value={
                profile.gender
                  ? genderLabels[profile.gender] ?? profile.gender
                  : null
              }
            />
            <InfoRow
              icon={CalendarDays}
              label="Возраст"
              value={age ? `${age} лет` : null}
            />
            <InfoRow
              icon={Ruler}
              label="Рост"
              value={profile.height_cm ? `${profile.height_cm} см` : null}
            />
            <InfoRow
              icon={Scale}
              label="Вес"
              value={profile.weight_kg ? `${profile.weight_kg} кг` : null}
            />
            <InfoRow
              icon={Trophy}
              label="Уровень подготовки"
              value={
                experienceLabels[profile.experience_level] ??
                profile.experience_level
              }
            />
            <InfoRow
              icon={Dumbbell}
              label="Уровень активности"
              value={
                profile.activity_level
                  ? activityLabels[profile.activity_level] ??
                    profile.activity_level
                  : null
              }
            />
          </div>
        </CardContent>
      </Card>

      {/* Goals card */}
      <Card className="border-border/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Target className="size-5 text-green-500" />
            <CardTitle>Цели</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-border/50">
            <InfoRow
              icon={Target}
              label="Основная цель"
              value={
                profile.goal
                  ? goalLabels[profile.goal] ?? profile.goal
                  : null
              }
            />
            <InfoRow
              icon={Scale}
              label="Целевой вес"
              value={
                profile.target_weight_kg
                  ? `${profile.target_weight_kg} кг`
                  : null
              }
            />
            <InfoRow
              icon={Dumbbell}
              label="Вид спорта"
              value={
                profile.sport_type
                  ? sportLabels[profile.sport_type] ?? profile.sport_type
                  : null
              }
            />
            <InfoRow
              icon={CalendarDays}
              label="Тренировочных дней в неделю"
              value={profile.training_days_per_week}
            />
          </div>
        </CardContent>
      </Card>

      {/* Medical restrictions card */}
      <Card className="border-border/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Heart className="size-5 text-red-500" />
            <CardTitle>Медицинские ограничения</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {profile.medical_restrictions.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {profile.medical_restrictions.map(
                (restriction: MedicalRestriction) => (
                  <div
                    key={restriction.id}
                    className="rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2"
                  >
                    <p className="text-sm font-medium">{restriction.description || restriction.name}</p>
                  </div>
                )
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Медицинские ограничения не указаны
            </p>
          )}
          {profile.custom_health_notes && (
            <div className="mt-4 rounded-lg border border-yellow-500/20 bg-yellow-500/5 p-3">
              <div className="flex items-center gap-2 text-sm font-medium">
                <NotebookPen className="size-4 text-yellow-500" />
                Дополнительные заметки
              </div>
              <p className="mt-1 text-sm text-muted-foreground">{profile.custom_health_notes}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dietary preferences card */}
      <Card className="border-border/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <UtensilsCrossed className="size-5 text-orange-500" />
            <CardTitle>Диетические предпочтения</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-border/50">
            <InfoRow
              icon={UtensilsCrossed}
              label="Приёмов пищи в день"
              value={profile.meals_per_day}
            />
            <InfoRow
              icon={AlertTriangle}
              label="Аллергии и непереносимости"
              value={profile.food_allergies || null}
            />
            <InfoRow
              icon={ThumbsDown}
              label="Нелюбимые продукты"
              value={profile.disliked_foods || null}
            />
          </div>
        </CardContent>
      </Card>

      {/* Danger zone */}
      <Separator />
      <Card className="border-destructive/30">
        <CardContent className="flex flex-col gap-4 pt-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-medium">Выйти из аккаунта</p>
            <p className="text-sm text-muted-foreground">
              Вы будете перенаправлены на страницу входа
            </p>
          </div>
          <Button
            variant="destructive"
            onClick={handleLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <LogOut className="size-4" />
            )}
            Выйти из аккаунта
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
