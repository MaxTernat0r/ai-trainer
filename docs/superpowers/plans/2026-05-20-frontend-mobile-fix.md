# Frontend Mobile Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Сделать все страницы Coach AI корректно работающими на мобильных устройствах от 320px без горизонтального скролла, обрезанного контента и сломанных интеракций.

**Architecture:** Локальные правки в layout-файлах, страницах и точечные правила в `globals.css`. Tailwind-классы `sm/md/lg`, без редизайна. Sheet-компонент (уже в репо) для мобильного сайдбара чата. Удаление AuthViewportLock-хака в пользу натурального скролла.

**Tech Stack:** Next.js 16 App Router, Tailwind 4, shadcn/Radix UI, Playwright (для верификации), pytest для backend test-helper.

**Spec:** `docs/superpowers/specs/2026-05-20-frontend-mobile-fix-design.md`

---

## File Structure

### Файлы, которые меняем

**Layouts (Группа A):**
- `frontend/src/app/(marketing)/layout.tsx` — снять `h-dvh overflow-hidden`
- `frontend/src/app/(marketing)/page.tsx` — мобильный flow, исправить грид карточек
- `frontend/src/app/(auth)/layout.tsx` — упростить, убрать `AuthViewportLock`
- `frontend/src/app/(dashboard)/layout.tsx` — `safe-area-inset-bottom`, убрать chat-исключение
- `frontend/src/app/(onboarding)/onboarding/page.tsx` — скрыть stepper-кружки на мобиле
- `frontend/src/app/globals.css` — отключить matrix-bursts на мобиле

**Удаляем:**
- `frontend/src/components/auth/auth-viewport-lock.tsx`

**Страницы dashboard (Группа B):**
- `frontend/src/app/(dashboard)/chat/page.tsx` — sheet-сайдбар для мобилы, sticky input
- `frontend/src/app/(dashboard)/dashboard/page.tsx` — адаптивные размеры значений

**Страницы данных (Группа C):**
- `frontend/src/app/(dashboard)/exercises/page.tsx` — фильтры flex-1 на мобиле
- `frontend/src/app/(dashboard)/analytics/page.tsx` — TabsList horizontal scroll
- `frontend/src/app/(dashboard)/workouts/page.tsx` — calendar truncate, hide checkmark на мобиле
- `frontend/src/app/(dashboard)/workouts/[workoutId]/page.tsx` — input width на мобиле
- `frontend/src/app/(dashboard)/nutrition/page.tsx` — адаптивные размеры

**Тестирование (Группа D):**
- `backend/scripts/seed_test_user.py` — новый: создаёт тестового верифицированного пользователя для Playwright
- `frontend/tests/mobile.spec.ts` — новый Playwright тест-файл
- `frontend/playwright.config.ts` — новый
- `frontend/package.json` — добавить deps + npm-script

**Деплой:**
- финальный `scripts/deploy_vps.sh root@147.45.149.215 /opt/ai-trainer` после успешных тестов.

---

## Заметка про Email Verification для тестов

Production имеет `EMAIL_VERIFICATION_REQUIRED=true`. Для локального тестирования через Playwright создаём backend-скрипт `backend/scripts/seed_test_user.py`, который:
1. Создаёт пользователя `mobile-test@coach-ai.local` с паролем
2. Ставит `is_verified=True` напрямую в БД
3. Создаёт полный профиль (все поля для прохождения onboarding gate)

Это **не обходит** verification на проде — только готовит фикстуру для локальных тестов. Production деплой не зависит от этого скрипта.

---

## Group A — Layouts & Global Styles

Группа A может выполняться полностью параллельно с группами B и C, потому что меняет независимые файлы. Внутри группы — последовательно.

### Task A1: Marketing layout — снять lock

**Files:**
- Modify: `frontend/src/app/(marketing)/layout.tsx`

- [ ] **Step 1: Заменить layout на скроллящийся**

```tsx
import type { ReactNode } from "react";

export default function MarketingLayout({ children }: { children: ReactNode }) {
  return <main className="min-h-dvh">{children}</main>;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/(marketing)/layout.tsx
git commit -m "fix(marketing): убрать h-dvh overflow-hidden для мобильного скролла"
```

### Task A2: Marketing page — flow на мобиле

**Files:**
- Modify: `frontend/src/app/(marketing)/page.tsx`

- [ ] **Step 1: Полная замена страницы**

Заменить файл на:

```tsx
import Link from "next/link";
import {
  ArrowRight,
  Dumbbell,
  LineChart,
  MessageSquare,
  ShieldCheck,
  Target,
  UtensilsCrossed,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const productCards = [
  {
    icon: Dumbbell,
    title: "Тренировочный план",
    text: "Coach AI собирает программу под цель, уровень, график и доступное оборудование.",
  },
  {
    icon: LineChart,
    title: "Мониторинг",
    text: "На данных тренировок, веса, питания и восстановления строятся графики нагрузки и прогресса.",
  },
  {
    icon: UtensilsCrossed,
    title: "Питание и вес",
    text: "Калории, белки и динамика веса становятся частью общего спортивного плана.",
  },
  {
    icon: MessageSquare,
    title: "ИИ-тренер",
    text: "Можно уточнить технику, заменить упражнение или адаптировать план под состояние.",
  },
];

const productFlow = [
  ["01", "цель", "Coach AI понимает задачу и стартовые данные"],
  ["02", "план", "формирует тренировки, питание и контрольные точки"],
  ["03", "адаптация", "корректирует рекомендации по фактическому прогрессу"],
];

export default function LandingPage() {
  return (
    <section className="relative z-10 mx-auto flex min-h-dvh max-w-7xl flex-col gap-4 px-4 py-6 sm:gap-6 sm:px-6 sm:py-8 lg:grid lg:h-dvh lg:grid-cols-[0.82fr_1.18fr] lg:items-center lg:gap-6 lg:py-0 lg:px-8">
      <div className="relative z-10 flex flex-col text-center lg:text-left">
        <div className="mb-3 flex flex-wrap justify-center gap-2 lg:justify-start">
          <span className="status-pill">Coach AI</span>
          <span className="status-pill">спортивный менеджер</span>
        </div>

        <h1 className="mx-auto max-w-3xl text-[2rem] font-semibold leading-[1.05] sm:text-5xl lg:mx-0 xl:text-7xl">
          Личный спортивный менеджер
        </h1>

        <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground sm:mt-4 sm:text-lg sm:leading-7 lg:mx-0">
          Coach AI превращает цель в понятную систему: тренировки, питание,
          нагрузка, восстановление и прогресс в одном маршруте.
        </p>

        <Button size="lg" asChild className="neon-action mx-auto mt-5 w-full max-w-xs sm:mt-7 lg:mx-0">
          <Link href="/register">
            <span className="relative z-10 flex items-center gap-2">
              Собрать личный план
              <ArrowRight className="size-4" />
            </span>
          </Link>
        </Button>
      </div>

      <div className="cockpit-panel panel-reveal relative rounded-lg p-3 sm:p-4 lg:min-h-0 lg:overflow-hidden">
        <div className="flex flex-col lg:h-full lg:min-h-0">
          <div className="flex shrink-0 items-start justify-between gap-4 border-b border-[#712031]/55 pb-3">
            <div className="min-w-0">
              <p className="tactical-readout text-[0.58rem] text-muted-foreground sm:text-[0.66rem]">
                продуктовая система
              </p>
              <h2 className="mt-1 text-base font-semibold leading-tight sm:text-2xl">
                Что Coach AI берет на себя
              </h2>
            </div>
            <div className="hidden items-center gap-2 sm:flex">
              {[ShieldCheck, Target].map((Icon, index) => (
                <div
                  key={index}
                  className="glass-lane interactive-lane flex size-10 items-center justify-center rounded-lg"
                >
                  <Icon className="size-4 text-primary" />
                </div>
              ))}
            </div>
          </div>

          <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 sm:gap-3 lg:min-h-0 lg:flex-1">
            {productCards.map((card) => (
              <div
                key={card.title}
                className="glass-lane interactive-lane flex flex-col rounded-lg p-3 sm:p-4 lg:min-h-0"
              >
                <div className="mb-2 flex items-center justify-between gap-2">
                  <card.icon className="size-4 shrink-0 text-primary sm:size-5" />
                  <span className="h-px flex-1 bg-[#712031]/55" />
                </div>
                <h3 className="text-sm font-semibold leading-tight sm:text-base">
                  {card.title}
                </h3>
                <p className="mt-1 text-[0.78rem] leading-5 text-muted-foreground sm:mt-2 sm:text-sm sm:leading-5">
                  {card.text}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-3 shrink-0 overflow-hidden rounded-lg border border-[#712031]/50">
            {productFlow.map(([step, title, text]) => (
              <div
                key={step}
                className="grid grid-cols-[auto_auto_1fr] gap-2 border-b border-[#712031]/40 px-3 py-2 text-xs last:border-b-0 sm:gap-3 sm:text-sm"
              >
                <span className="tactical-readout text-[0.6rem] text-primary sm:text-[0.64rem]">
                  {step}
                </span>
                <span className="font-semibold whitespace-nowrap">{title}</span>
                <span className="text-muted-foreground">{text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Lint+build**

Run: `cd frontend && npm run lint`
Expected: PASS, нет ошибок

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/(marketing)/page.tsx
git commit -m "fix(marketing): мобильный flow лендинга, productFlow на всех viewport"
```

### Task A3: Удалить AuthViewportLock

**Files:**
- Delete: `frontend/src/components/auth/auth-viewport-lock.tsx`
- Modify: `frontend/src/app/(auth)/layout.tsx`

- [ ] **Step 1: Удалить файл AuthViewportLock**

Run: `rm frontend/src/components/auth/auth-viewport-lock.tsx`

- [ ] **Step 2: Упростить auth layout**

Заменить файл `frontend/src/app/(auth)/layout.tsx` на:

```tsx
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="flex min-h-dvh items-center justify-center px-3 py-6 sm:px-6 sm:py-10">
      <div className="panel-reveal w-full max-w-md">
        {children}
      </div>
    </main>
  );
}
```

- [ ] **Step 3: Проверить, что нет других импортов AuthViewportLock**

Run: `grep -rn "auth-viewport-lock\|AuthViewportLock" frontend/src/`
Expected: пусто

- [ ] **Step 4: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/auth/auth-viewport-lock.tsx frontend/src/app/(auth)/layout.tsx
git commit -m "fix(auth): убрать body-position-fixed хак, естественный скролл при клавиатуре"
```

### Task A4: Dashboard layout — safe-area, убрать chat-исключение

**Files:**
- Modify: `frontend/src/app/(dashboard)/layout.tsx`

- [ ] **Step 1: Изменить main и nav**

В `(dashboard)/layout.tsx` найти блок:

```tsx
        {/* Page content */}
        <main
          ref={contentRef}
          className={cn(
            'no-scrollbar flex-1',
            isChatPage
              ? 'overflow-hidden pb-0'
              : 'overflow-y-auto pb-24 md:pb-0'
          )}
        >
          <div
            className={cn(
              'mx-auto max-w-[1500px] p-1 sm:p-0',
              isChatPage && 'h-full min-h-0'
            )}
          >
            {children}
          </div>
        </main>
```

Заменить на:

```tsx
        {/* Page content */}
        <main
          ref={contentRef}
          className={cn(
            'no-scrollbar flex-1 overflow-y-auto pb-[calc(5rem+env(safe-area-inset-bottom))] md:pb-0',
            isChatPage && 'md:overflow-hidden'
          )}
        >
          <div
            className={cn(
              'mx-auto max-w-[1500px] p-1 sm:p-0',
              isChatPage && 'md:h-full md:min-h-0'
            )}
          >
            {children}
          </div>
        </main>
```

И блок:

```tsx
      <nav className="cockpit-panel fixed inset-x-2 bottom-2 z-50 rounded-lg md:hidden">
        <div className="flex items-center justify-around py-2">
```

Заменить на:

```tsx
      <nav className="cockpit-panel fixed inset-x-2 bottom-[max(0.5rem,env(safe-area-inset-bottom))] z-50 rounded-lg md:hidden">
        <div className="flex items-center justify-around py-2">
```

- [ ] **Step 2: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/(dashboard)/layout.tsx
git commit -m "fix(dashboard): safe-area для таб-бара, убрать chat-исключение в pb"
```

### Task A5: Globals — выключить matrix-bursts на мобиле

**Files:**
- Modify: `frontend/src/app/globals.css`

- [ ] **Step 1: Расширить @media (max-width: 767px)**

В `globals.css` найти блок:

```css
@media (max-width: 767px) {
  body::before {
    animation-duration: 46s;
  }

  body::after {
    opacity: 0.24;
    animation-duration: 30s;
  }

  .cockpit-panel,
  .glass-lane {
    backdrop-filter: none;
  }

  .panel-reveal {
    animation-duration: 280ms;
  }
}
```

Заменить на:

```css
@media (max-width: 767px) {
  body::before {
    animation-duration: 46s;
  }

  body::after {
    opacity: 0.24;
    animation-duration: 30s;
  }

  .global-matrix-field {
    display: none;
  }

  .cockpit-panel,
  .glass-lane {
    backdrop-filter: none;
  }

  .panel-reveal {
    animation-duration: 280ms;
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/globals.css
git commit -m "perf(css): выключить matrix-bursts на мобильных для GPU/батареи"
```

### Task A6: Onboarding stepper — скрыть кружки на мобиле

**Files:**
- Modify: `frontend/src/app/(onboarding)/onboarding/page.tsx`

- [ ] **Step 1: Скрыть ряд кружков**

Найти блок (строки 243-257):

```tsx
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
              {i < step ? <Check className="size-4" /> : <s.icon className="size-4" />}
            </div>
          ))}
        </div>
```

Заменить первую строку на:

```tsx
        <div className="hidden justify-between sm:flex">
```

(остальное без изменений)

- [ ] **Step 2: Commit**

```bash
git add frontend/src/app/(onboarding)/onboarding/page.tsx
git commit -m "fix(onboarding): скрыть stepper-кружки на узких экранах, прогресс-бар достаточен"
```

---

## Group B — Chat & Dashboard pages

Может выполняться параллельно с группами A и C. Внутри — последовательно.

### Task B1: Chat — мобильный сайдбар через Sheet

**Files:**
- Modify: `frontend/src/app/(dashboard)/chat/page.tsx`

- [ ] **Step 1: Добавить импорты Sheet и MenuIcon**

В `chat/page.tsx` найти импорт `lucide-react`:

```tsx
import {
  Send,
  MessageSquare,
  Plus,
  Bot,
  User,
  Dumbbell,
  UtensilsCrossed,
  HelpCircle,
  PanelLeftClose,
  PanelLeft,
  Loader2,
  Trash2,
} from 'lucide-react';
```

Добавить `Menu`:

```tsx
import {
  Send,
  MessageSquare,
  Plus,
  Bot,
  User,
  Dumbbell,
  UtensilsCrossed,
  HelpCircle,
  PanelLeftClose,
  PanelLeft,
  Loader2,
  Trash2,
  Menu,
} from 'lucide-react';
```

И добавить импорт Sheet после строки с `import { Skeleton }`:

```tsx
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
```

- [ ] **Step 2: Добавить state для мобильного сайдбара**

В компоненте `ChatPage`, после строки `const [sidebarVisible, setSidebarVisible] = useState(true);` добавить:

```tsx
const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
```

- [ ] **Step 3: Извлечь ConversationsList в локальный JSX**

В `chat/page.tsx` сейчас содержимое сайдбара (`<aside>` со списком диалогов) дублируется только в desktop. Чтобы переиспользовать в Sheet, выделим в локальную переменную внутри компонента, ДО `return`:

```tsx
const conversationsListContent = (
  <div className="flex h-full flex-col">
    <div className="flex shrink-0 items-center justify-between border-b border-[#712031]/55 p-4">
      <h2 className="font-semibold">Диалоги</h2>
      <Button
        variant="ghost"
        size="icon-xs"
        onClick={() => {
          handleNewConversation();
          setMobileSidebarOpen(false);
        }}
        disabled={createConversation.isPending}
      >
        {createConversation.isPending ? (
          <Loader2 className="size-4 animate-spin" />
        ) : (
          <Plus className="size-4" />
        )}
      </Button>
    </div>
    <div className="no-scrollbar min-h-0 flex-1 overflow-y-auto p-3">
      <div className="flex flex-col gap-2">
        {conversationsLoading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="glass-lane flex items-center gap-3 rounded-lg px-3 py-2.5">
                <Skeleton className="size-4 shrink-0 rounded" />
                <div className="min-w-0 flex-1">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="mt-1 h-3 w-20" />
                </div>
              </div>
            ))}
          </>
        ) : conversations && conversations.length > 0 ? (
          conversations.map((conv) => (
            <div
              key={conv.id}
              role="button"
              tabIndex={0}
              onClick={() => {
                setActiveConversationId(conv.id);
                setMobileSidebarOpen(false);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setActiveConversationId(conv.id);
                  setMobileSidebarOpen(false);
                }
              }}
              className={cn(
                'group glass-lane flex cursor-pointer items-center gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-200',
                activeConversationId === conv.id
                  ? 'border-primary/45 bg-primary/12 shadow-[inset_0_1px_0_rgb(255_255_255_/_8%),0_0_20px_rgb(255_0_48_/_10%)]'
                  : 'border-[#712031]/30 hover:border-primary/35 hover:bg-white/[0.055]'
              )}
            >
              <MessageSquare
                className={cn(
                  'size-4 shrink-0',
                  activeConversationId === conv.id
                    ? 'text-primary'
                    : 'text-muted-foreground'
                )}
              />
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">
                  {conv.title ?? 'Новый диалог'}
                </p>
                <p className="text-xs text-muted-foreground">
                  {new Date(conv.created_at).toLocaleDateString('ru-RU')}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon-xs"
                className="shrink-0 opacity-60 transition-opacity hover:opacity-100"
                onClick={(e) => handleDeleteConversation(conv.id, e)}
              >
                <Trash2 className="size-3 text-muted-foreground" />
              </Button>
            </div>
          ))
        ) : (
          <p className="px-3 py-6 text-center text-sm text-muted-foreground">
            Нет диалогов. Создайте новый!
          </p>
        )}
      </div>
    </div>
  </div>
);
```

- [ ] **Step 4: Заменить desktop aside и chat header**

Найти существующий блок `<aside ...>...</aside>` (строки 180-277) — заменить на:

```tsx
{/* Sidebar - desktop only */}
<aside
  className={cn(
    'hidden min-h-0 flex-col border-r border-[#712031]/55 bg-black/[0.18] transition-all duration-300',
    sidebarVisible ? 'md:flex md:w-80' : 'md:hidden'
  )}
>
  <div className="flex shrink-0 items-center justify-between border-b border-[#712031]/55 p-4">
    <h2 className="font-semibold">Диалоги</h2>
    <div className="flex items-center gap-1">
      <Button
        variant="ghost"
        size="icon-xs"
        onClick={handleNewConversation}
        disabled={createConversation.isPending}
      >
        {createConversation.isPending ? (
          <Loader2 className="size-4 animate-spin" />
        ) : (
          <Plus className="size-4" />
        )}
      </Button>
      <Button
        variant="ghost"
        size="icon-xs"
        onClick={() => setSidebarVisible(false)}
      >
        <PanelLeftClose className="size-4" />
      </Button>
    </div>
  </div>
  <div className="no-scrollbar min-h-0 flex-1 overflow-y-auto p-3">
    <div className="flex flex-col gap-2">
      {conversationsLoading ? (
        <>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="glass-lane flex items-center gap-3 rounded-lg px-3 py-2.5">
              <Skeleton className="size-4 shrink-0 rounded" />
              <div className="min-w-0 flex-1">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="mt-1 h-3 w-20" />
              </div>
            </div>
          ))}
        </>
      ) : conversations && conversations.length > 0 ? (
        conversations.map((conv) => (
          <div
            key={conv.id}
            role="button"
            tabIndex={0}
            onClick={() => setActiveConversationId(conv.id)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                setActiveConversationId(conv.id);
              }
            }}
            className={cn(
              'group glass-lane flex cursor-pointer items-center gap-3 rounded-lg border px-3 py-2.5 text-left text-sm transition-all duration-200',
              activeConversationId === conv.id
                ? 'border-primary/45 bg-primary/12 shadow-[inset_0_1px_0_rgb(255_255_255_/_8%),0_0_20px_rgb(255_0_48_/_10%)]'
                : 'border-[#712031]/30 hover:border-primary/35 hover:bg-white/[0.055]'
            )}
          >
            <MessageSquare
              className={cn(
                'size-4 shrink-0',
                activeConversationId === conv.id
                  ? 'text-primary'
                  : 'text-muted-foreground'
              )}
            />
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">
                {conv.title ?? 'Новый диалог'}
              </p>
              <p className="text-xs text-muted-foreground">
                {new Date(conv.created_at).toLocaleDateString('ru-RU')}
              </p>
            </div>
            <Button
              variant="ghost"
              size="icon-xs"
              className="pointer-events-none shrink-0 opacity-0 transition-opacity group-hover:pointer-events-auto group-hover:opacity-100"
              onClick={(e) => handleDeleteConversation(conv.id, e)}
            >
              <Trash2 className="size-3 text-muted-foreground" />
            </Button>
          </div>
        ))
      ) : (
        <p className="px-3 py-6 text-center text-sm text-muted-foreground">
          Нет диалогов. Создайте новый!
        </p>
      )}
    </div>
  </div>
</aside>
```

- [ ] **Step 5: Добавить мобильную кнопку в chat header**

Найти строку с chat header (`<div className="flex shrink-0 items-center gap-3 border-b border-[#712031]/55 px-4 py-3">`). Внутри заменить блок (где сейчас начинается с `{!sidebarVisible && (`) на:

```tsx
          <Sheet open={mobileSidebarOpen} onOpenChange={setMobileSidebarOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon-xs" className="md:hidden">
                <Menu className="size-4" />
                <span className="sr-only">Открыть список диалогов</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80 max-w-[85vw] p-0">
              <SheetHeader className="sr-only">
                <SheetTitle>Диалоги</SheetTitle>
              </SheetHeader>
              {conversationsListContent}
            </SheetContent>
          </Sheet>
          {!sidebarVisible && (
            <Button
              variant="ghost"
              size="icon-xs"
              className="hidden md:inline-flex"
              onClick={() => setSidebarVisible(true)}
            >
              <PanelLeft className="size-4" />
            </Button>
          )}
```

- [ ] **Step 6: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add frontend/src/app/(dashboard)/chat/page.tsx
git commit -m "feat(chat): мобильный сайдбар диалогов через Sheet"
```

### Task B2: Dashboard cards — адаптивные размеры

**Files:**
- Modify: `frontend/src/app/(dashboard)/dashboard/page.tsx`

- [ ] **Step 1: Уменьшить text-3xl на мобиле**

Открыть `dashboard/page.tsx`, найти стат-карточки и заменить `text-3xl` (в значениях статов) на `text-2xl sm:text-3xl`. Используем replace_all для безопасности — он заменит все вхождения в файле (это нужный эффект, т.к. все text-3xl относятся к стат-значениям).

Найти все строки `text-3xl font-semibold` и заменить на `text-2xl font-semibold sm:text-3xl`.

- [ ] **Step 2: min-h-[148px] → min-h на мобиле меньше**

Найти строку:

```tsx
                className="panel-reveal min-h-[148px]"
```

Заменить на:

```tsx
                className="panel-reveal min-h-[120px] sm:min-h-[148px]"
```

- [ ] **Step 3: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/(dashboard)/dashboard/page.tsx
git commit -m "fix(dashboard): адаптивные размеры стат-карточек на мобиле"
```

---

## Group C — Data pages

Может выполняться параллельно с группами A и B. Внутри — последовательно.

### Task C1: Exercises — фильтры flex-1 на мобиле

**Files:**
- Modify: `frontend/src/app/(dashboard)/exercises/page.tsx`

- [ ] **Step 1: Изменить SelectTrigger для всех 4 фильтров**

В `exercises/page.tsx`:

Заменить `<SelectTrigger className="w-[160px]">` (2 вхождения) на:

```tsx
<SelectTrigger className="w-full min-w-[8rem] flex-1 sm:w-[160px] sm:flex-none">
```

Заменить `<SelectTrigger className="w-[180px]">` (2 вхождения) на:

```tsx
<SelectTrigger className="w-full min-w-[8rem] flex-1 sm:w-[180px] sm:flex-none">
```

- [ ] **Step 2: Изменить контейнер фильтров**

Найти `<div className="flex flex-wrap gap-3">` и заменить на:

```tsx
<div className="grid grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:gap-3">
```

Это даст на мобиле 2-колоночный грид с фильтрами, на sm+ — старый flex-wrap.

- [ ] **Step 3: Кнопка «Сбросить» на мобиле full-width в отдельной строке**

Найти блок:

```tsx
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
```

Заменить на:

```tsx
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            className="col-span-2 sm:col-span-1"
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
```

- [ ] **Step 4: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/(dashboard)/exercises/page.tsx
git commit -m "fix(exercises): фильтры в 2 колонки на мобиле"
```

### Task C2: Analytics — TabsList горизонтальный скролл

**Files:**
- Modify: `frontend/src/app/(dashboard)/analytics/page.tsx`

- [ ] **Step 1: TabsList → scroll wrapper**

Найти блок:

```tsx
      <Tabs defaultValue="weight" className="w-full">
        <TabsList className="w-full sm:w-auto">
```

Заменить на:

```tsx
      <Tabs defaultValue="weight" className="w-full">
        <div className="no-scrollbar -mx-1 overflow-x-auto px-1">
          <TabsList className="inline-flex w-max min-w-full sm:w-auto sm:min-w-0">
```

И найти **закрывающий** `</TabsList>` (он один на странице) и заменить на:

```tsx
          </TabsList>
        </div>
```

(закрытие `</div>` сразу после `</TabsList>`)

Также: убедиться, что у TabsTrigger в этой группе нет `flex-1` который бы мешал сжатию. Проверим — сейчас есть `<TabsTrigger value="weight" className="gap-1.5">`. Без flex-1, ок.

- [ ] **Step 2: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/(dashboard)/analytics/page.tsx
git commit -m "fix(analytics): TabsList с горизонтальным скроллом на мобиле"
```

### Task C3: Workouts list calendar — truncate, hide checkmark

**Files:**
- Modify: `frontend/src/app/(dashboard)/workouts/page.tsx`

- [ ] **Step 1: min-w-0 на ячейке календаря**

Найти блок (около строки 562):

```tsx
                  <div
                    key={idx}
                    className={`relative min-h-[72px] rounded-md border p-1 text-xs ${
```

Заменить на:

```tsx
                  <div
                    key={idx}
                    className={`relative min-h-[72px] min-w-0 rounded-md border p-1 text-xs ${
```

- [ ] **Step 2: Найти entry-блок с checkmark кнопкой**

Найти (около строки 588-600):

```tsx
                            {cell.entries?.map((entry) => (
                              <div
                                key={entry.id}
                                className={`group/entry flex items-center gap-1 rounded px-1 py-0.5 text-[10px] leading-tight ${
                                  entry.is_completed
                                    ? 'bg-primary/12 text-primary'
                                    : 'bg-primary/10 text-primary'
                                }`}
                              >
                                <button
                                  className="shrink-0 rounded p-0.5 transition-colors hover:bg-muted/50"
                                  title={entry.is_completed ? 'Отметить как невыполненную' : 'Отметить как выполненную'}
```

Изменить класс кнопки `shrink-0 rounded p-0.5 ...` на:

```
hidden shrink-0 rounded p-0.5 transition-colors hover:bg-muted/50 sm:inline-flex
```

(одно изменение: добавить `hidden ... sm:inline-flex`)

- [ ] **Step 3: Truncate на названии entry**

Сразу после кнопки в том же блоке должна быть `<span>` или `<Link>` с названием упражнения. Это уже после строки в выдаче — продолжение строки 600+. Найти первый `<span>` или текст внутри `entry`-div и убедиться, что у него класс `truncate min-w-0`. Если нет — добавить.

Если структура такая `<button>...<span>{entry.title}</span>...</button>` — добавить `className="truncate"` к span.

- [ ] **Step 4: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/(dashboard)/workouts/page.tsx
git commit -m "fix(workouts): truncate в ячейках календаря, скрыть checkmark на мобиле"
```

### Task C4: Workout session — input width на мобиле

**Files:**
- Modify: `frontend/src/app/(dashboard)/workouts/[workoutId]/page.tsx`

- [ ] **Step 1: Изменить ширину input weight/reps**

Найти 2 строки:

```tsx
                          className="h-9 w-24"
```

Заменить на (через replace_all — обе строки одинаковы и обе нужно заменить):

```tsx
                          className="h-9 w-16 sm:w-24"
```

- [ ] **Step 2: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add frontend/src/app/(dashboard)/workouts/[workoutId]/page.tsx
git commit -m "fix(workout-session): уменьшить input weight/reps на мобиле"
```

### Task C5: Nutrition — адаптивные размеры

**Files:**
- Modify: `frontend/src/app/(dashboard)/nutrition/page.tsx`

- [ ] **Step 1: Найти места с большими цифрами в маленьких ячейках**

Прочитать `nutrition/page.tsx` целиком (945 строк), найти все вхождения `text-3xl`, `text-2xl` в контексте grid-cells. Заменить:
- `text-3xl` (когда внутри `grid-cols-2` или `grid-cols-3`) → `text-2xl sm:text-3xl`
- `text-2xl` (когда внутри `grid-cols-3` или `grid-cols-4`) → `text-xl sm:text-2xl`

- [ ] **Step 2: Конкретные места**

Файл прочитать. Найти строки с шаблоном `grid grid-cols-3 gap-` и проверить, какой размер шрифта внутри. Применить адаптивность.

- [ ] **Step 3: Lint**

Run: `cd frontend && npm run lint`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add frontend/src/app/(dashboard)/nutrition/page.tsx
git commit -m "fix(nutrition): адаптивные размеры цифр в КБЖУ-ячейках"
```

---

## Group D — Build, test setup, verification

Должна выполняться **после** A, B, C (зависит от их завершения).

### Task D1: Build all changes

**Files:** none

- [ ] **Step 1: Frontend lint + build**

Run: `cd frontend && npm run lint && npm run build`
Expected: PASS, успешная сборка standalone

Если падает — починить ошибки прежде чем идти дальше. Не пропускать.

### Task D2: Backend test-user seeder

**Files:**
- Create: `backend/scripts/seed_test_user.py`

- [ ] **Step 1: Написать seed-скрипт**

Содержимое `backend/scripts/seed_test_user.py`:

```python
"""Создать тестового пользователя для Playwright-тестов мобильной адаптивности.

Запуск из backend/:
    python -m scripts.seed_test_user

Создаёт пользователя mobile-test@coach-ai.local с паролем mobile-test-pass-123,
ставит is_verified=True, заполняет профиль (все поля для прохождения onboarding gate).

Идемпотентен: при повторном запуске обновляет пароль и профиль.
"""
import asyncio
from datetime import date

from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.user import User
from app.models.profile import UserProfile
from sqlalchemy import select

TEST_EMAIL = "mobile-test@coach-ai.local"
TEST_PASSWORD = "mobile-test-pass-123"


async def main() -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == TEST_EMAIL))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                email=TEST_EMAIL,
                password_hash=hash_password(TEST_PASSWORD),
                is_verified=True,
                is_active=True,
            )
            session.add(user)
            await session.flush()
            print(f"Created user {TEST_EMAIL}")
        else:
            user.password_hash = hash_password(TEST_PASSWORD)
            user.is_verified = True
            user.is_active = True
            print(f"Updated user {TEST_EMAIL}")

        prof_result = await session.execute(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
        profile = prof_result.scalar_one_or_none()

        profile_data = dict(
            first_name="Mobile",
            last_name="Tester",
            date_of_birth=date(1995, 6, 15),
            gender="male",
            height_cm=180,
            weight_kg=80,
            goal="general_fitness",
            sport_type="gym",
            experience_level="intermediate",
            activity_level="moderate",
            training_days_per_week=3,
            equipment_available="full_gym",
            target_weight_kg=78,
            meals_per_day=3,
        )

        if profile is None:
            profile = UserProfile(user_id=user.id, **profile_data)
            session.add(profile)
            print("Created profile")
        else:
            for key, value in profile_data.items():
                setattr(profile, key, value)
            print("Updated profile")

        await session.commit()
        print(f"Test user ready. Email: {TEST_EMAIL}, password: {TEST_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Запустить локальный backend и seed**

Run в backend/: убедиться что DB поднята (через docker compose), затем:

```bash
cd backend
docker compose up -d db redis
alembic upgrade head
python -m scripts.seed_db
python -m scripts.seed_test_user
```

Expected: все три команды успешны, последняя печатает `Test user ready.`

Если что-то падает — посмотреть, что именно (миграция/импорт), починить, повторить. Не двигаться дальше пока не работает.

- [ ] **Step 3: Commit**

```bash
git add backend/scripts/seed_test_user.py
git commit -m "test(backend): seed-скрипт верифицированного тест-пользователя для Playwright"
```

### Task D3: Setup Playwright

**Files:**
- Create: `frontend/playwright.config.ts`
- Modify: `frontend/package.json`

- [ ] **Step 1: Установить Playwright**

```bash
cd frontend && npm install -D @playwright/test && npx playwright install chromium webkit
```

Expected: успешная установка.

- [ ] **Step 2: Создать `frontend/playwright.config.ts`**

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'mobile-320',
      use: { ...devices['iPhone SE'], viewport: { width: 320, height: 568 } },
    },
    {
      name: 'mobile-375',
      use: { ...devices['iPhone 12'], viewport: { width: 375, height: 667 } },
    },
    {
      name: 'mobile-414',
      use: { ...devices['iPhone 14 Pro Max'], viewport: { width: 414, height: 896 } },
    },
  ],
});
```

- [ ] **Step 3: Добавить npm-script**

В `frontend/package.json` блок `"scripts":` добавить:

```json
"test:mobile": "playwright test",
"test:mobile:headed": "playwright test --headed"
```

- [ ] **Step 4: Создать `.gitignore` записи**

Добавить в `frontend/.gitignore` (если не существуют):

```
test-results/
playwright-report/
playwright/.cache/
```

- [ ] **Step 5: Commit**

```bash
git add frontend/playwright.config.ts frontend/package.json frontend/package-lock.json frontend/.gitignore
git commit -m "test(frontend): setup Playwright для мобильных тестов"
```

### Task D4: Mobile test suite

**Files:**
- Create: `frontend/tests/mobile.spec.ts`
- Create: `frontend/tests/helpers/auth.ts`

- [ ] **Step 1: Auth helper**

Создать `frontend/tests/helpers/auth.ts`:

```ts
import type { Page } from '@playwright/test';

export const TEST_EMAIL = 'mobile-test@coach-ai.local';
export const TEST_PASSWORD = 'mobile-test-pass-123';

export async function loginAsTestUser(page: Page): Promise<void> {
  await page.goto('/login');
  await page.fill('input[type=email], input[name=email]', TEST_EMAIL);
  await page.fill('input[type=password], input[name=password]', TEST_PASSWORD);
  await page.click('button[type=submit]');
  await page.waitForURL((url) => !url.pathname.includes('/login'), { timeout: 10000 });
}

export async function expectNoHorizontalScroll(page: Page): Promise<void> {
  const overflow = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  if (overflow.scrollWidth > overflow.clientWidth) {
    throw new Error(
      `Horizontal scroll detected: scrollWidth=${overflow.scrollWidth} clientWidth=${overflow.clientWidth}`
    );
  }
}
```

- [ ] **Step 2: Создать `frontend/tests/mobile.spec.ts`**

```ts
import { test, expect } from '@playwright/test';
import { loginAsTestUser, expectNoHorizontalScroll } from './helpers/auth';

const PUBLIC_PAGES = [
  { path: '/', name: 'landing' },
  { path: '/login', name: 'login' },
  { path: '/register', name: 'register' },
];

const PRIVATE_PAGES = [
  { path: '/dashboard', name: 'dashboard' },
  { path: '/workouts', name: 'workouts' },
  { path: '/nutrition', name: 'nutrition' },
  { path: '/chat', name: 'chat' },
  { path: '/exercises', name: 'exercises' },
  { path: '/analytics', name: 'analytics' },
  { path: '/profile', name: 'profile' },
];

test.describe('Public pages mobile layout', () => {
  for (const page of PUBLIC_PAGES) {
    test(`${page.name} fits viewport without horizontal scroll`, async ({ page: pw }, testInfo) => {
      await pw.goto(page.path);
      await pw.waitForLoadState('networkidle');
      await expectNoHorizontalScroll(pw);
      await pw.screenshot({
        path: `test-results/screenshots/${testInfo.project.name}-${page.name}.png`,
        fullPage: true,
      });
    });
  }
});

test.describe('Private pages mobile layout', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsTestUser(page);
  });

  for (const p of PRIVATE_PAGES) {
    test(`${p.name} fits viewport without horizontal scroll`, async ({ page: pw }, testInfo) => {
      await pw.goto(p.path);
      await pw.waitForLoadState('networkidle');
      await expectNoHorizontalScroll(pw);
      await pw.screenshot({
        path: `test-results/screenshots/${testInfo.project.name}-${p.name}.png`,
        fullPage: true,
      });
    });
  }
});

test.describe('Critical mobile interactions', () => {
  test('chat sidebar opens via Sheet on mobile', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/chat');
    await page.waitForLoadState('networkidle');
    const menuButton = page.locator('button:has(svg.lucide-menu), button[aria-label*="диалог" i]').first();
    await expect(menuButton).toBeVisible();
    await menuButton.click();
    await expect(page.locator('[data-slot="sheet-content"]')).toBeVisible();
  });

  test('dashboard tab bar is not hidden by safe-area', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    const tabBar = page.locator('nav.fixed').filter({ hasText: 'Главная' }).first();
    await expect(tabBar).toBeVisible();
    const box = await tabBar.boundingBox();
    expect(box).not.toBeNull();
    if (box) {
      const viewport = page.viewportSize();
      expect(box.y + box.height).toBeLessThanOrEqual(viewport!.height);
    }
  });
});
```

- [ ] **Step 3: Commit**

```bash
git add frontend/tests/
git commit -m "test(frontend): mobile layout suite — overflow checks + screenshots"
```

### Task D5: Run mobile tests

**Files:** none

- [ ] **Step 1: Запустить backend**

В отдельном терминале:

```bash
cd backend
source venv/bin/activate  # или venv/.venv/bin/activate
uvicorn app.main:app --port 8000
```

Backend должен висеть. Если не запускается — починить, ничего не пропуская.

- [ ] **Step 2: Запустить frontend dev server**

В другом терминале:

```bash
cd frontend && npm run dev
```

Дождаться `Ready in...`. Frontend на http://localhost:3000.

- [ ] **Step 3: Прогнать тесты**

В третьем терминале:

```bash
cd frontend && npm run test:mobile
```

Expected: все тесты PASS на трёх проектах (mobile-320, mobile-375, mobile-414). Скрины в `test-results/screenshots/`.

Если тесты падают — для каждого падающего:
1. Посмотреть, на каком viewport падает.
2. Прочитать стек / скрин.
3. Найти соответствующую страницу/компонент в коде и доработать.
4. Прогнать тест точечно: `npm run test:mobile -- --project=mobile-320 -g "exercises"`
5. Перезапустить весь suite после фикса.

Не двигаться к следующему таску пока **все** тесты не зелёные на всех viewport.

- [ ] **Step 4: Просмотреть скрины глазами**

Открыть `test-results/screenshots/` и быстро пробежать каждый файл. На что смотреть:
- Контент не обрезан
- Заголовки читаются
- Кнопки не наслаиваются
- Грид-структура целая

Если нашёл косяк, не пойманный авто-проверкой (например, наезды текста, нечитаемый контраст) — **создать новый коммит** с фиксом. Не амендить.

### Task D6: Final lint + build

**Files:** none

- [ ] **Step 1: Lint**

```bash
cd frontend && npm run lint
```

Expected: PASS, 0 ошибок и 0 warning'ов в наших новых файлах.

- [ ] **Step 2: Production build**

```bash
cd frontend && npm run build
```

Expected: успешная standalone-сборка.

### Task D7: Re-run mobile tests against fresh build

**Files:** none

- [ ] **Step 1: Stop dev server, start production build**

```bash
cd frontend && npm run start
```

(на http://localhost:3000, но уже из `.next/standalone`)

- [ ] **Step 2: Прогнать тесты ещё раз против production-сборки**

В другом терминале:

```bash
cd frontend && PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:mobile
```

Expected: все тесты PASS. Скрины обновлены.

Если есть отличия от dev-режима (что бывает редко, но случается с CSS-extracts, hydration mismatches) — починить и повторить.

---

## Group E — Deploy to production

Выполнять только после полного зелёного D7.

### Task E1: Push and deploy

**Files:** none

- [ ] **Step 1: Push в main**

```bash
cd /Users/a1234/Documents/projects/ai-trainer
git status
git log --oneline origin/main..HEAD
git push origin main
```

Expected: успешный push.

- [ ] **Step 2: Деплой на VPS**

```bash
scripts/deploy_vps.sh root@147.45.149.215 /opt/ai-trainer
```

Expected: успешный деплой. Скрипт сам:
- rsync репо
- build образов
- alembic upgrade head
- seed_db
- restart всех сервисов
- проверка nginx + certbot

- [ ] **Step 3: Production smoke**

```bash
backend/.venv/bin/python scripts/prod_smoke.py --base-url https://coach-ai.ru
```

Expected: все 23 кейса PASS. Если есть падения — это могут быть **не** наши изменения (мы фронт трогали), но всё равно проверить.

- [ ] **Step 4: Прогнать Playwright против production**

```bash
cd frontend && PLAYWRIGHT_BASE_URL=https://coach-ai.ru npm run test:mobile -- --project=mobile-375 -g "Public"
```

Только публичные страницы — для приватных нужен seed test-user'а на проде, чего мы не хотим. Public-проверки достаточно.

Expected: все public тесты PASS на проде.

- [ ] **Step 5: Финальный отчёт пользователю**

Сообщить пользователю:
- Что задеплоено
- Линк https://coach-ai.ru
- Что прошли все локальные тесты (3 viewport × 10 страниц)
- Что прошли smoke-тесты прода
- Что прошли Playwright против прода (public)
- Просьба проверить с iPhone на трёх ключевых страницах (landing, register, dashboard) — поскольку реальный девайс может вскрыть то, что emulated viewport не вскрыл (notch, dynamic island, safari URL bar quirks).

---

## Self-Review Checklist

Прошёл по spec'у:

| Spec пункт | Покрытие |
|---|---|
| G1 marketing layout | Task A1 |
| G2 marketing page | Task A2 |
| G3 auth viewport lock | Task A3 |
| G4 safe-area tab bar | Task A4 |
| G5 chat-исключение pb | Task A4 |
| G6 matrix-bursts | Task A5 |
| P1 onboarding stepper | Task A6 |
| P2 exercises filters | Task C1 |
| P3 chat sidebar mobile | Task B1 |
| P4 chat input pb | Task A4 (вместе с G5) |
| P5 analytics tabs | Task C2 |
| P6 workout session input | Task C4 |
| P7 workouts calendar | Task C3 |
| P8 nutrition sizes | Task C5 |
| P9 dashboard sizes | Task B2 |
| Email verification обход для тестов | Task D2 (seed_test_user) |
| Verification (Playwright + screenshots) | Tasks D3-D7 |
| Deploy | Task E1 |

Все пункты покрыты. Email verification на проде **остаётся включённой** — обход только для локального тестирования через seed-скрипт.

## Параллелизация (для subagent-driven-development)

Зависимости:
- A1, A2, A3, A4, A5, A6 — все независимы между собой и от B/C → можно гонять параллельно
- B1, B2 — независимы между собой и от A/C → можно гонять параллельно
- C1, C2, C3, C4, C5 — независимы между собой и от A/B → можно гонять параллельно
- D1 (build) — после **всех** A, B, C
- D2 (seed) — может параллельно с любым из A/B/C
- D3 (Playwright setup) — может параллельно с D2
- D4 (test suite) — после D3
- D5 (run tests) — после D1, D2, D4
- D6, D7 — последовательно после D5
- E1 — последний, после D7

В оптимальной параллелизации:
- Wave 1 (параллельно): A1, A2, A3, A4, A5, A6, B1, B2, C1, C2, C3, C4, C5, D2, D3
- Wave 2: D1 (build), D4 (test suite — пишется на основе плана, не зависит от A/B/C)
- Wave 3: D5 (тесты)
- Wave 4: D6, D7 (rebuild + re-test)
- Wave 5: E1 (deploy)
