'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { authApi } from '@/lib/api/auth';
import { useAuthStore } from '@/lib/stores/auth-store';
import { Loader2, LockKeyhole, Mail } from 'lucide-react';
import { toast } from 'sonner';
import { HTTPError } from 'ky';

const registerSchema = z
  .object({
    email: z.string().email('Введите корректный email'),
    password: z.string().min(6, 'Пароль должен содержать минимум 6 символов'),
    confirmPassword: z.string().min(1, 'Подтвердите пароль'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Пароли не совпадают',
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const setAuth = useAuthStore((state) => state.setAuth);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      const registerResponse = await authApi.register(data.email, data.password);
      if (!registerResponse.requires_verification) {
        const loginResponse = await authApi.login(data.email, data.password);
        setAuth(loginResponse.access_token, loginResponse.user);
        toast.success('Аккаунт создан');
        window.location.href = '/dashboard';
        return;
      }

      window.sessionStorage.setItem('pendingVerificationEmail', data.email);
      toast.success('Мы отправили письмо для подтверждения email');
      window.location.href = `/verify-email?email=${encodeURIComponent(data.email)}`;
    } catch (error) {
      if (error instanceof HTTPError) {
        const body = await error.response.json().catch(() => null);
        if (body?.error?.code === 'EMAIL_SERVICE_ERROR') {
          toast.error('Не удалось отправить код подтверждения. Попробуйте позже.');
          return;
        }
        if (body?.error?.code === 'BAD_REQUEST') {
          toast.error(body.error.message);
          return;
        }
      }
      toast.error('Ошибка при регистрации. Возможно, email уже занят.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border-[rgb(var(--theme-shade-rgb)/65%)]">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Регистрация</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="email" className="flex items-center gap-2">
              <Mail className="size-4 text-primary" />
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              {...register('email')}
              aria-invalid={!!errors.email}
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email.message}</p>
            )}
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="password" className="flex items-center gap-2">
              <LockKeyhole className="size-4 text-primary" />
              Пароль
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              {...register('password')}
              aria-invalid={!!errors.password}
            />
            {errors.password && (
              <p className="text-sm text-destructive">
                {errors.password.message}
              </p>
            )}
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="confirmPassword" className="flex items-center gap-2">
              <LockKeyhole className="size-4 text-primary" />
              Подтвердите пароль
            </Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="••••••••"
              {...register('confirmPassword')}
              aria-invalid={!!errors.confirmPassword}
            />
            {errors.confirmPassword && (
              <p className="text-sm text-destructive">
                {errors.confirmPassword.message}
              </p>
            )}
          </div>
          <Button type="submit" className="priority-action mt-2 w-full" disabled={isLoading}>
            {isLoading && <Loader2 className="animate-spin" />}
            Создать аккаунт
          </Button>
        </form>

      </CardContent>
      <CardFooter className="justify-center">
        <p className="text-sm text-muted-foreground">
          Уже есть аккаунт?{' '}
          <Link
            href="/login"
            className="font-medium text-primary underline-offset-4 hover:underline"
          >
            Войдите
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}
