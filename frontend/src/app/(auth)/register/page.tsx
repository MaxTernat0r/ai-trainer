'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
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
import { authApi } from '@/lib/api/auth';
import { useAuthStore } from '@/lib/stores/auth-store';
import { Dumbbell, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

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
  const router = useRouter();
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
      const response = await authApi.register(data.email, data.password);
      setAuth(response.access_token, response.user);
      toast.success('Аккаунт успешно создан');
      window.location.href = '/onboarding';
    } catch {
      toast.error('Ошибка при регистрации. Возможно, email уже занят.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border-border/50">
      <CardHeader className="text-center">
        <div className="mx-auto mb-2 flex size-12 items-center justify-center rounded-full bg-primary/10">
          <Dumbbell className="size-6 text-primary" />
        </div>
        <CardTitle className="text-2xl">Регистрация</CardTitle>
        <CardDescription>
          Создайте аккаунт и начните тренироваться
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="email">Email</Label>
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
            <Label htmlFor="password">Пароль</Label>
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
            <Label htmlFor="confirmPassword">Подтвердите пароль</Label>
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
          <Button type="submit" className="mt-2 w-full" disabled={isLoading}>
            {isLoading && <Loader2 className="animate-spin" />}
            Создать аккаунт
          </Button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-border" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card px-2 text-muted-foreground">
              или через
            </span>
          </div>
        </div>

        <div className="flex flex-col gap-3">
          <Button variant="outline" className="w-full" type="button">
            <svg className="size-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Google
          </Button>
          <Button variant="outline" className="w-full" type="button">
            <svg className="size-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2 12C2 6.48 6.48 2 12 2s10 4.48 10 10-4.48 10-10 10S2 17.52 2 12zm10.8-4.4H7.6v3.2h3.04c-.16 1.44-1.36 2.72-3.04 2.72-1.84 0-3.36-1.52-3.36-3.52s1.52-3.52 3.36-3.52c.96 0 1.68.32 2.24.88l1.6-1.6C10.32 4.72 8.96 4 7.6 4 4.48 4 2 6.48 2 9.6s2.48 5.6 5.6 5.6c3.2 0 5.36-2.24 5.36-5.44 0-.4 0-.72-.16-1.16z" />
            </svg>
            Яндекс
          </Button>
          <Button variant="outline" className="w-full" type="button">
            <svg className="size-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12.785 16.241s.288-.032.436-.194c.136-.148.132-.427.132-.427s-.02-1.304.587-1.496c.596-.19 1.362 1.26 2.174 1.82.613.42 1.08.328 1.08.328l2.17-.03s1.135-.07.596-.962c-.044-.073-.314-.662-1.618-1.872-1.365-1.268-1.182-1.062.462-3.254 1-.335 1.762-2.7 1.762-2.7s.058-.462-.406-.66c-.468-.2-1.27-.06-1.27-.06l-2.443.016s-.181-.025-.316.056c-.131.079-.216.262-.216.262s-.387 1.028-.903 1.904c-1.088 1.848-1.524 1.946-1.702 1.832-.413-.267-.31-1.075-.31-1.648 0-1.792.272-2.538-.53-2.732-.266-.064-.462-.107-1.142-.114-.873-.009-1.612.003-2.03.208-.278.136-.493.44-.362.457.162.022.528.099.722.363.25.341.24 1.107.24 1.107s.144 2.11-.335 2.372c-.33.18-.78-.187-1.748-1.862-.495-.858-.87-1.808-.87-1.808s-.071-.176-.2-.271c-.155-.116-.374-.153-.374-.153l-2.32.015s-.348.01-.476.161c-.114.134-.009.412-.009.412s1.82 4.258 3.882 6.403c1.89 1.967 4.038 1.837 4.038 1.837z" />
            </svg>
            VK
          </Button>
        </div>
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
