'use client';

import { type FormEvent, Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { HTTPError } from 'ky';
import { CheckCircle2, Loader2, MailCheck, Send } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { authApi } from '@/lib/api/auth';
import { useAuthStore } from '@/lib/stores/auth-store';

type VerifyState = 'waiting' | 'verifying' | 'verified' | 'error';

function maskEmail(email: string): string {
  const [name, domain] = email.split('@');
  if (!name || !domain) return email;

  const visibleName = name.length <= 2 ? name[0] : name.slice(0, 2);
  return `${visibleName}${'*'.repeat(Math.max(2, name.length - visibleName.length))}@${domain}`;
}

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const setAuth = useAuthStore((state) => state.setAuth);
  const token = searchParams.get('token');
  const initialEmail = searchParams.get('email') ?? '';
  const [email, setEmail] = useState(initialEmail);
  const [code, setCode] = useState('');
  const [state, setState] = useState<VerifyState>(token ? 'verifying' : 'waiting');
  const [isResending, setIsResending] = useState(false);
  const [isVerifyingCode, setIsVerifyingCode] = useState(false);

  useEffect(() => {
    if (initialEmail) {
      window.sessionStorage.setItem('pendingVerificationEmail', initialEmail);
      return;
    }

    const storedEmail = window.sessionStorage.getItem('pendingVerificationEmail');
    if (storedEmail) {
      setEmail(storedEmail);
    }
  }, [initialEmail]);

  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    const verificationToken = token;

    async function verify() {
      setState('verifying');
      try {
        const response = await authApi.verifyEmail({ token: verificationToken });
        if (cancelled) return;
        setAuth(response.access_token, response.user);
        window.sessionStorage.removeItem('pendingVerificationEmail');
        setState('verified');
        toast.success('Email подтвержден');
        window.setTimeout(() => {
          window.location.href = '/onboarding';
        }, 700);
      } catch (error) {
        if (cancelled) return;
        setState('error');
        if (error instanceof HTTPError && error.response.status === 400) {
          toast.error('Ссылка подтверждения недействительна или устарела');
          return;
        }
        toast.error('Не удалось подтвердить email');
      }
    }

    verify();

    return () => {
      cancelled = true;
    };
  }, [setAuth, token]);

  const verifyCode = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!email) {
      toast.error('Email для подтверждения не найден');
      return;
    }

    const normalizedCode = code.replace(/\D/g, '');
    if (normalizedCode.length !== 6) {
      toast.error('Введите 6-значный код');
      return;
    }

    setIsVerifyingCode(true);
    setState('verifying');
    try {
      const response = await authApi.verifyEmail({ email, code: normalizedCode });
      setAuth(response.access_token, response.user);
      window.sessionStorage.removeItem('pendingVerificationEmail');
      setState('verified');
      toast.success('Email подтвержден');
      window.setTimeout(() => {
        window.location.href = '/onboarding';
      }, 700);
    } catch (error) {
      setState('error');
      if (error instanceof HTTPError && error.response.status === 400) {
        toast.error('Код недействителен или устарел');
        return;
      }
      toast.error('Не удалось подтвердить email');
    } finally {
      setIsVerifyingCode(false);
    }
  };

  const resend = async () => {
    if (!email) {
      toast.error('Email для подтверждения не найден');
      return;
    }

    setIsResending(true);
    try {
      await authApi.resendVerification(email);
      toast.success('Если аккаунт найден, мы отправили новое письмо');
    } catch {
      toast.error('Не удалось отправить письмо');
    } finally {
      setIsResending(false);
    }
  };

  const icon =
    state === 'verified' ? (
      <CheckCircle2 className="size-6 text-primary" />
    ) : state === 'verifying' ? (
      <Loader2 className="size-6 animate-spin text-primary" />
    ) : (
      <MailCheck className="size-6 text-primary" />
    );

  return (
    <Card className="border-[rgb(var(--theme-shade-rgb)/65%)]">
      <CardHeader className="text-center">
        <div className="mx-auto mb-3 flex size-12 items-center justify-center rounded-lg border border-primary/35 bg-primary/12 shadow-[0_0_20px_rgb(190_24_42_/_14%)]">
          {icon}
        </div>
        <div className="mx-auto mb-2">
          <span className="status-pill">mail checkpoint</span>
        </div>
        <CardTitle className="text-2xl">
          {state === 'verifying'
            ? 'Подтверждаем email'
            : state === 'verified'
              ? 'Email подтвержден'
              : 'Проверьте почту'}
        </CardTitle>
        <CardDescription>
          {state === 'error'
            ? 'Код мог устареть. Проверьте код или отправьте новый.'
            : state === 'verified'
              ? 'Сейчас перенаправим вас к настройке профиля.'
              : email
                ? `Мы отправили код на ${maskEmail(email)}.`
                : 'Вернитесь к регистрации, чтобы получить код подтверждения.'}
        </CardDescription>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        {(state === 'waiting' || state === 'error') && email && (
          <form onSubmit={verifyCode} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="verification-code">Код подтверждения</Label>
              <Input
                id="verification-code"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                pattern="[0-9]*"
                maxLength={6}
                value={code}
                onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                className="text-center text-xl font-semibold tracking-[0.35em]"
              />
            </div>
            <Button type="submit" disabled={isVerifyingCode}>
              {isVerifyingCode && <Loader2 className="animate-spin" />}
              Подтвердить email
            </Button>
            <Button type="button" variant="outline" onClick={resend} disabled={isResending}>
              {isResending ? <Loader2 className="animate-spin" /> : <Send />}
              Отправить код повторно
            </Button>
          </form>
        )}
        {(state === 'waiting' || state === 'error') && !email && (
          <Button asChild>
            <Link href="/register">Вернуться к регистрации</Link>
          </Button>
        )}
      </CardContent>

      <CardFooter className="justify-center">
        <p className="text-sm text-muted-foreground">
          Уже подтвердили?{' '}
          <Link
            href="/login"
            className="font-medium text-primary underline-offset-4 hover:underline"
          >
            Войти
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <Card className="border-[rgb(var(--theme-shade-rgb)/65%)]">
          <CardHeader className="text-center">
            <div className="mx-auto mb-3 flex size-12 items-center justify-center rounded-lg border border-primary/35 bg-primary/12">
              <Loader2 className="size-6 animate-spin text-primary" />
            </div>
            <CardTitle className="text-2xl">Загружаем</CardTitle>
          </CardHeader>
        </Card>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
