'use client';

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
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import type { User } from '@/types/user';
import type { Profile, MedicalRestriction } from '@/types/user';

// --- Mock data ---
const mockUser: User = {
  id: 'u1',
  email: 'ivan.petrov@email.com',
  is_active: true,
  is_verified: true,
  avatar_url: null,
};

const mockProfile: Profile = {
  id: 'p1',
  first_name: 'Иван',
  last_name: 'Петров',
  date_of_birth: '1995-06-15',
  gender: 'male',
  height_cm: 180,
  weight_kg: 78.5,
  experience_level: 'intermediate',
  goal: 'muscle_gain',
  sport_type: 'bodybuilding',
  activity_level: 'moderate',
  target_weight_kg: 85,
  equipment_available: 'full_gym',
  training_days_per_week: 4,
  medical_restrictions: [
    {
      id: 'mr1',
      name: 'Проблемы с поясницей',
      description: 'Грыжа L4-L5, избегать осевых нагрузок на позвоночник',
    },
  ],
};

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
};

const sportLabels: Record<string, string> = {
  bodybuilding: 'Бодибилдинг',
  powerlifting: 'Пауэрлифтинг',
  crossfit: 'Кроссфит',
  calisthenics: 'Калистеника',
  general: 'Общая физ. подготовка',
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
      <span className="text-sm font-medium">{value ?? '---'}</span>
    </div>
  );
}

export default function ProfilePage() {
  const fullName =
    [mockProfile.first_name, mockProfile.last_name].filter(Boolean).join(' ') ||
    'Не указано';
  const memberSince = '15 марта 2025';
  const age = mockProfile.date_of_birth
    ? Math.floor(
        (Date.now() - new Date(mockProfile.date_of_birth).getTime()) /
          (365.25 * 24 * 60 * 60 * 1000)
      )
    : null;

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
          {mockUser.avatar_url ? (
            <img
              src={mockUser.avatar_url}
              alt="Avatar"
              className="size-full rounded-full object-cover"
            />
          ) : (
            <UserIcon className="size-10 text-primary" />
          )}
        </div>
        <div>
          <h2 className="text-xl font-bold">{fullName}</h2>
          <p className="text-sm text-muted-foreground">{mockUser.email}</p>
          <div className="mt-1 flex items-center gap-2">
            {mockUser.is_verified && (
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
            <InfoRow icon={Mail} label="Email" value={mockUser.email} />
            <InfoRow
              icon={CalendarDays}
              label="Дата регистрации"
              value={memberSince}
            />
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
                mockProfile.gender
                  ? genderLabels[mockProfile.gender] ?? mockProfile.gender
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
              value={
                mockProfile.height_cm ? `${mockProfile.height_cm} см` : null
              }
            />
            <InfoRow
              icon={Scale}
              label="Вес"
              value={
                mockProfile.weight_kg ? `${mockProfile.weight_kg} кг` : null
              }
            />
            <InfoRow
              icon={Trophy}
              label="Уровень подготовки"
              value={
                experienceLabels[mockProfile.experience_level] ??
                mockProfile.experience_level
              }
            />
            <InfoRow
              icon={Dumbbell}
              label="Уровень активности"
              value={
                mockProfile.activity_level
                  ? activityLabels[mockProfile.activity_level] ??
                    mockProfile.activity_level
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
                mockProfile.goal
                  ? goalLabels[mockProfile.goal] ?? mockProfile.goal
                  : null
              }
            />
            <InfoRow
              icon={Scale}
              label="Целевой вес"
              value={
                mockProfile.target_weight_kg
                  ? `${mockProfile.target_weight_kg} кг`
                  : null
              }
            />
            <InfoRow
              icon={Dumbbell}
              label="Вид спорта"
              value={
                mockProfile.sport_type
                  ? sportLabels[mockProfile.sport_type] ?? mockProfile.sport_type
                  : null
              }
            />
            <InfoRow
              icon={CalendarDays}
              label="Тренировочных дней в неделю"
              value={mockProfile.training_days_per_week}
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
          {mockProfile.medical_restrictions.length > 0 ? (
            <div className="flex flex-col gap-3">
              {mockProfile.medical_restrictions.map(
                (restriction: MedicalRestriction) => (
                  <div
                    key={restriction.id}
                    className="rounded-lg border border-red-500/20 bg-red-500/5 p-3"
                  >
                    <p className="text-sm font-medium">{restriction.name}</p>
                    {restriction.description && (
                      <p className="mt-1 text-xs text-muted-foreground">
                        {restriction.description}
                      </p>
                    )}
                  </div>
                )
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Медицинские ограничения не указаны
            </p>
          )}
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
          <Button variant="destructive">
            <LogOut className="size-4" />
            Выйти из аккаунта
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
