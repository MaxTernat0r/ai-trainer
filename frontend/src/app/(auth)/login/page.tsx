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

const loginSchema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(6, 'Пароль должен содержать минимум 6 символов'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const setAuth = useAuthStore((state) => state.setAuth);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      const response = await authApi.login(data.email, data.password);
      setAuth(response.access_token, response.user);
      toast.success('Вы успешно вошли в аккаунт');
      window.location.href = '/dashboard';
    } catch (error) {
      if (error instanceof HTTPError && error.response.status === 403) {
        const body = await error.response.json().catch(() => null);
        if (body?.error?.code === 'EMAIL_NOT_VERIFIED') {
          toast.error('Сначала подтвердите email');
          window.location.href = `/verify-email?email=${encodeURIComponent(data.email)}`;
          return;
        }
      }
      toast.error('Неверный email или пароль');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border-[#712031]/65">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">Авторизация</CardTitle>
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
          <Button type="submit" className="mt-2 w-full" disabled={isLoading}>
            {isLoading && <Loader2 className="animate-spin" />}
            Войти
          </Button>
        </form>

      </CardContent>
      <CardFooter className="justify-center">
        <p className="text-sm text-muted-foreground">
          Нет аккаунта?{' '}
          <Link
            href="/register"
            className="font-medium text-primary underline-offset-4 hover:underline"
          >
            Зарегистрируйтесь
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}
