# Frontend Mobile Fix — Design

Дата: 2026-05-20
Статус: спека для реализации
Минимальный целевой viewport: **320px** (iPhone 5/SE 1ген)
Тестовые viewport'ы: 320×568, 375×667, 414×896

## Цель

Сделать так, чтобы все публичные и dashboard-страницы Coach AI корректно отображались на мобильных устройствах от 320px шириной без горизонтального скролла, обрезанного контента, перекрытий нижним таб-баром и сломанных интеракций. Без редизайна и без изменений бэкенда.

## Не делаем

- Новый UI / визуальный редизайн страниц
- Изменения функциональности и API
- Правки auth flow / refresh / cookie
- 3D-визуализация (R3F не подключён к страницам)
- Новые мобильные жесты (swipe-to-delete и т.п.)

## Найденные проблемы

### Глобальные (layout-уровень)

| # | Файл | Проблема | Симптом |
|---|---|---|---|
| G1 | `app/(marketing)/layout.tsx` | `h-dvh overflow-hidden` лочит лендинг в высоту экрана | На мобиле контент обрезается снизу под URL-bar; не скроллится |
| G2 | `app/(marketing)/page.tsx` | Внутренняя сетка тоже `h-full overflow-hidden` с фиксированными `grid-cols-2` для карточек | На 320–375px карточки тесные, нечитаемые; flow `productFlow` спрятан за `hidden sm:block` |
| G3 | `app/(auth)/layout.tsx` + `components/auth/auth-viewport-lock.tsx` | Хак с `position: fixed` на body + кастомным touchmove handler | Известно ломает фокус инпутов при появлении клавиатуры на iOS Safari, jumpы на Android, не нужен при правильно настроенных скроллах |
| G4 | `app/(dashboard)/layout.tsx` | Нижний таб-бар `fixed inset-x-2 bottom-2` без `safe-area-inset-bottom` | На iPhone X+ home indicator перекрывает иконки |
| G5 | `app/(dashboard)/layout.tsx` (chat-исключение) | Для `/chat` главный `<main>` имеет `pb-0`, при этом нижний таб-бар фиксирован | Поле ввода чата перекрывается таб-баром на мобиле |
| G6 | `app/globals.css` (matrix-bursts) | 12 декоративных burst-элементов с `clip-path`, мульти-градиентами, `filter: drop-shadow` рендерятся на каждой странице | На дешёвых Android — лаги, нагрев, расход батареи |

### Постраничные

| # | Страница | Проблема | На каком viewport ломается |
|---|---|---|---|
| P1 | `(onboarding)/onboarding/page.tsx` стэппер | 8 кружков `size-8` через `flex justify-between` | <328px — не помещаются; на 375 впритык |
| P2 | `(dashboard)/exercises/page.tsx` | 4 фильтра-Select c фиксированной шириной `w-[160px]` × 2 + `w-[180px]` × 2 в `flex-wrap` | На 320 фильтры разъезжаются на 4 строки, неаккуратно |
| P3 | `(dashboard)/chat/page.tsx` сайдбар | `aside` с классами `sidebarVisible ? 'hidden w-80 md:flex' : 'hidden'` | На мобиле сайдбар не доступен в принципе — нельзя выбрать другой диалог |
| P4 | `(dashboard)/chat/page.tsx` инпут | См. G5 — пересекается с таб-баром | На мобиле |
| P5 | `(dashboard)/analytics/page.tsx` | `TabsList` с 5 табами, у каждого иконка + текст | На 320–375 не помещается, ломает layout |
| P6 | `(dashboard)/workouts/[workoutId]/page.tsx` | Таблица сетов: badge + Input(weight) + Input(reps) + Button = ~430px | Уже есть `overflow-x-auto`, но горизонталка появляется на 320–414, что не идеально для основного flow тренировки |
| P7 | `(dashboard)/workouts/page.tsx` календарь | `grid-cols-7` × 46px ячейки на 320px, текст entries `text-[10px]` с кнопкой переключения | Кнопка checkmark (`shrink-0`) внутри ячейки может выпадать; день-номер впритык |
| P8 | `(dashboard)/nutrition/page.tsx` | Несколько мест с `grid-cols-2 sm:grid-cols-4` и `grid-cols-3 gap-4` | На 320 цифры КБЖУ с лейблами могут наезжать друг на друга |
| P9 | `(dashboard)/dashboard/page.tsx` | `min-h-[148px]` карточки + `text-3xl` значения в `grid-cols-2` | Длинные числа (4+ цифр) могут вылезать |

## Подход к починке

### G1, G2 — Marketing landing

- В `(marketing)/layout.tsx`: `h-dvh overflow-hidden` → `min-h-dvh`. Естественный скролл.
- В `(marketing)/page.tsx`: убрать обёртку `h-full overflow-hidden`; root `section` поменять с `grid-rows-[auto_minmax(0,1fr)]` на flex column с естественным flow на мобиле, грид только на `lg:`.
- Карточки `productCards`: `grid-cols-1 sm:grid-cols-2` (вместо текущего `grid-cols-2` сразу).
- `productFlow` показывать на мобиле тоже (убрать `hidden sm:block`), просто компактно.

### G3 — Auth viewport lock

- Удалить `auth-viewport-lock.tsx` и его использование в `(auth)/layout.tsx`.
- Layout переписать как: `min-h-dvh flex items-center justify-center px-4 py-8`. Без `position: fixed`, без кастомных touchmove. Естественный скролл, страница нормально дышит при клавиатуре.
- `body { overflow-x: hidden; min-h-dvh }` (уже есть в globals) даёт нужный bounce-минимум.

### G4 — Safe-area для таб-бара

- В `(dashboard)/layout.tsx` нижний `<nav>`: добавить `pb-[env(safe-area-inset-bottom)]` или сместить `bottom-[max(0.5rem,env(safe-area-inset-bottom))]`.

### G5, P3, P4 — Chat-страница на мобиле

Самая большая правка после auth.

- Убрать «исключение для chat» в layout: всегда `pb-24 md:pb-0` на main, чтобы инпут чата не уходил под таб-бар.
- Сделать инпут чата `sticky bottom-0` с фоном или просто оставить во flow, но с правильным `pb` снизу.
- Сайдбар диалогов на мобиле: использовать существующий `components/ui/sheet.tsx` (он уже есть в репо). Кнопка-иконка в header chat-страницы открывает Sheet со списком диалогов. На `md:` остаётся inline-сайдбар как сейчас.

### G6 — Matrix-bursts на мобиле

- В `globals.css`: добавить в `@media (max-width: 767px)` блок `.global-matrix-field { display: none }` или хотя бы скрыть половину bursts. Анимации `body::before/::after` остаются (они уже замедлены).

### P1 — Onboarding stepper на мобиле

- Скрыть ряд кружков на узких экранах: `hidden sm:flex`.
- Прогресс-бар + текст «Шаг N из 8 — заголовок» уже есть выше — этого достаточно для мобилы.

### P2 — Exercises фильтры

- Убрать `w-[160px]`/`w-[180px]` на мобиле: `flex-1 min-w-[10rem] sm:flex-none sm:w-[160px]`.
- При этом `flex-wrap` остаётся — на широких будут в одну строку, на 320 в две колонки парами.

### P5 — Analytics tabs

- `TabsList` сделать горизонтально-скроллящимся на мобиле: `overflow-x-auto no-scrollbar` + дочерние `shrink-0`.
- Альтернатива: на мобиле скрыть текст табов, оставить иконки. Решим по визуалу — приоритет вариант 1 (скролл).

### P6 — Workout session table

- Оставить таблицу + `overflow-x-auto` (уже есть). Не превращать в карточки — это редизайн.
- Уменьшить ширину инпутов на мобиле: `w-24` → `w-16 sm:w-24` для weight и reps.
- На 320px горизонтальный скролл внутри таблицы остаётся допустимым (документированный компромисс) — главное чтобы он не выливался в горизонтальный скролл всей страницы.

### P7 — Workout calendar

- `grid-cols-7` помещается на 320 без overflow страницы, реальная проблема только в разборчивости подписей внутри ячейки.
- Применить `min-w-0` к ячейкам и `truncate` к названиям entries.
- На мобиле `text-[10px]` оставить, но скрыть checkmark-кнопку внутри ячейки (`hidden sm:inline-flex`) — переключение делается через переход на страницу тренировки.

### P8, P9 — nutrition/dashboard цифры

- Где есть большие значения в маленькой ячейке: `text-3xl` → `text-2xl sm:text-3xl`, `text-2xl` → `text-xl sm:text-2xl`.
- `grid-cols-3 gap-4` в одном месте nutrition (~3 ячейки) ок на 320 если уменьшить шрифт. Просто проследить.

## Архитектурные решения

- **Не делаем глобальный CSS reset под мобилу.** Все правки локальные — в layout-файлах, страницах, и единичные правила в `globals.css` для `@media (max-width: 767px)`.
- **Tailwind first.** Используем брейкпойнты `sm`/`md`/`lg`. Никаких inline-стилей.
- **Сохраняем текущую брендовую эстетику.** Только производительность (matrix-bursts на мобиле).
- **Sheet для chat-сайдбара.** Использовать существующий `@/components/ui/sheet`, не вводить новых зависимостей.
- **Не трогаем функциональные стейты.** Все Zustand stores, query hooks, формы остаются как есть.

## Контекст для параллельной работы

Изменения логически разбиваются на независимые группы — потенциально хорошо для параллельных субагентов в плане реализации:

- **Группа A (layouts + global)**: G1, G2, G3, G4, G6, P1 — все три layout'а + globals.css + onboarding stepper
- **Группа B (chat + dashboard)**: G5, P3, P4, P9 — chat-страница и dashboard cards
- **Группа C (data pages)**: P2, P5, P6, P7, P8 — exercises, analytics, workouts list, workout session, nutrition
- **Группа D (testing)**: после A/B/C — Playwright прогон по всем страницам в 320/375/414

Конкретное разбиение и порядок планирует writing-plans.

## Верификация

1. `cd frontend && npm run lint && npm run build` — ничего не должно сломаться
2. `cd frontend && npm run dev` — поднять dev server
3. Playwright скрипт обходит все основные страницы в viewport 320×568, 375×667, 414×896:
   - `/` (marketing landing)
   - `/login`, `/register`
   - `/onboarding` (для проверки нужен залогиненный неполный профиль — мокать через DOM, или просто пройти регистрацию заранее)
   - `/dashboard`, `/workouts`, `/workouts/[id]`, `/nutrition`, `/chat`, `/exercises`, `/analytics`, `/profile`
4. На каждом viewport: проверить отсутствие `document.documentElement.scrollWidth > window.innerWidth` (горизонтальный скролл).
5. Скриншоты прикладываются к финальному отчёту.

## Известные ограничения

- **Onboarding и dashboard-страницы требуют логина и заполненного профиля.** Для авто-теста в Playwright либо стабим API ответ профиля через route-interception, либо проходим регистрацию + email verification + onboarding программно. Простейший вариант: тестовый аккаунт + сидинг профиля прямо в локальную DB.
- **Workout session** требует существующего активного плана — для теста стабим `useActiveWorkoutPlan` через MSW или просто открываем страницу с моковым ответом.
- На 320px некоторые таблицы (workout-session) останутся с горизонтальным скроллом — это сознательный компромисс, документирован в P6.

## Риски

- **AuthViewportLock удаление**: возможно был добавлен из-за конкретного бага (вероятно iOS bounce). Регрессия может вернуть лёгкий bounce на login/register. Митигация: при удалении тестировать на iOS Safari (если нет железа — Playwright webkit).
- **Sheet в chat**: компонент уже есть, но если он использует Portal с body-scroll-lock несовместимым с нашим layout — могут быть конфликты. Митигация: посмотреть компонент перед использованием.
- **Marketing landing**: смена `h-dvh` на `min-h-dvh` поменяет ощущение страницы на десктопе — нужно сравнить визуально, но логика та же. Если десктоп выглядел зафиксированным «в один экран» специально — оставить `lg:h-dvh lg:overflow-hidden` для больших экранов и натуральный flow только на мобиле.
