# AI Trainer - Codex Project Context

Дата последнего разбора: 2026-05-19.

Этот файл нужен как рабочая память для будущих сессий Codex. Он не заменяет
`README.md`: README описывает продукт для человека, а здесь зафиксирована
архитектура, фактическое состояние кода, расхождения и безопасные следующие
шаги.

## Что это за проект

AI Trainer - русскоязычная веб-платформа для персональных тренировок, питания,
чата с ИИ-тренером и аналитики прогресса.

Монорепозиторий:

- `backend/` - FastAPI API, async SQLAlchemy, Alembic, OpenAI-сервисы.
- `frontend/` - Next.js App Router UI, TanStack Query, Zustand, Tailwind/shadcn.
- `nginx/` - reverse proxy для production-деплоя.
- `docker-compose.prod.yml` - production compose для VPS.

Текущая ветка при разборе: `main`, remote:
`https://github.com/MaxTernat0r/ai-trainer`.

## Стек по факту

Backend:

- Python 3.12, FastAPI `0.115.x`, Uvicorn.
- SQLAlchemy 2 async + asyncpg, PostgreSQL 16.
- Alembic migrations.
- AI provider abstraction: `AI_PROVIDER=auto|anthropic|openai`.
- OpenAI Python SDK сохранен, модель по умолчанию `gpt-5.4-mini`.
- Anthropic Messages API подключен через `httpx`; default model
  `claude-haiku-4-5-20251001`, поддержаны два ключа
  `ANTHROPIC_API_KEY` и `ANTHROPIC_API_KEY_2`.
- JWT access tokens + refresh tokens в БД, bcrypt/passlib.
- Redis указан в настройках/compose, но rate limiting/cache сейчас не подключены.
- `httpx[socks]` и `OPENAI_PROXY_URL` поддержаны в коде для OpenAI-прокси.

Frontend:

- По `package.json`: Next.js `16.1.6`, React `19.2.3`, TypeScript strict.
- Tailwind CSS 4, shadcn/Radix UI, lucide-react.
- TanStack Query v5 для server state.
- Zustand для auth/ui state.
- Recharts для графиков.
- Three.js/R3F компоненты есть, но в страницах не используются.

Infrastructure:

- `backend/docker-compose.yml` - локальный compose для backend/db/redis.
- `docker-compose.prod.yml` - production db/redis/backend/frontend/nginx/certbot.
- `nginx/nginx.conf` настроен под `coach-ai.ru` и `www.coach-ai.ru`.

Domain check 2026-05-19:

- `coach-ai.ru` и `www.coach-ai.ru` указывают на VPS `147.45.149.215`.
- HTTP редиректит на HTTPS; HTTPS отдаёт Next.js приложение.
- Let's Encrypt сертификат для `coach-ai.ru` и `www.coach-ai.ru` выпущен до
  `2026-08-17`.

## Быстрый запуск

Backend локально:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
alembic upgrade head
python -m scripts.seed_db
uvicorn app.main:app --reload --port 8000
```

Frontend локально:

```bash
cd frontend
npm install
npm run dev
```

Локальная БД/Redis через compose:

```bash
cd backend
docker compose up -d db redis
```

Production compose:

```bash
docker compose -f docker-compose.prod.yml up -d
```

Важное расхождение: в README указан `python -m app.scripts.seed_db`, но
фактический скрипт находится в `backend/scripts/seed_db.py`, поэтому из
`backend/` нужна команда `python -m scripts.seed_db`.

## Переменные окружения

Основные:

- `DATABASE_URL`
- `SECRET_KEY`
- `OPENAI_API_KEY`
- `REDIS_URL`
- `CORS_ORIGINS`
- `FRONTEND_URL`
- `EMAIL_VERIFICATION_REQUIRED` - `true` requires a 6-digit email code before
  login; `false` is only for emergency/demo bypass.
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`,
  `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME`, `SMTP_STARTTLS`,
  `SMTP_TLS_SERVER_HOSTNAME`, `SMTP_REQUIRED`
- `SMTP_PROXY_LISTEN_HOST`, `SMTP_PROXY_LISTEN_PORT`,
  `SMTP_PROXY_TARGET_HOST`, `SMTP_PROXY_TARGET_PORT`,
  `SMTP_PROXY_TARGET_FAMILY`
- `COOKIE_SECURE`, `COOKIE_SAMESITE`
- `AI_PROVIDER`
- `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_MINI_MODEL`
- `ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY_2`, `ANTHROPIC_API_KEYS`,
  `ANTHROPIC_MODEL`, `ANTHROPIC_TIMEOUT_SECONDS`
- `NEXT_PUBLIC_API_URL`
- `BACKEND_URL`

Дополнительно код поддерживает `OPENAI_PROXY_URL`, но в `.env.example` его нет.
Если нужен SOCKS/HTTP proxy для OpenAI, добавить туда явно.

Production compose ожидает `DOMAIN=coach-ai.ru`, задает
`NEXT_PUBLIC_API_URL=https://${DOMAIN}` и `BACKEND_URL=http://backend:8000`.
На текущем demo-деплое `EMAIL_VERIFICATION_REQUIRED=true`: регистрация отправляет
код на email, login до verify возвращает `403 EMAIL_NOT_VERIFIED`.
Nginx отдельно маршрутизирует:

- `/api/v1/...` -> backend FastAPI.
- `/api/auth/refresh` -> Next.js refresh proxy.
- `/openapi.json`, `/docs`, `/redoc` -> backend FastAPI docs.
- `/uploads/...` -> backend static uploads.

Для Gmail SMTP нужен Google App Password, обычный пароль Google не подойдет.
На Timeweb VPS IPv4 SMTP до Gmail таймаутится, а IPv6 с хоста работает. Поэтому
production compose запускает `smtp-proxy` с `network_mode: host`: он слушает
только Docker bridge `172.18.0.1:2525` и форвардит на `smtp.gmail.com:587` по
IPv6. Backend подключается к `SMTP_HOST=172.18.0.1`, `SMTP_PORT=2525`, но
проверяет TLS hostname через `SMTP_TLS_SERVER_HOSTNAME=smtp.gmail.com`.
UFW должен разрешать только `172.18.0.0/16 -> 172.18.0.1:2525`.
Backend settings читают `../.env` и `.env`, чтобы локальный запуск из папки
`backend/` видел корневой env, но локальный `backend/.env` мог переопределить
значения при необходимости.

## Backend architecture

Entry point:

- `backend/app/main.py` создает FastAPI app.
- Все роутеры подключены с префиксом `settings.API_V1_PREFIX`, по умолчанию
  `/api/v1`.
- CORS берет `settings.CORS_ORIGINS`.
- Кастомные ошибки идут через `app.core.exceptions.AppException`.

DB:

- `app/db/base_model.py` - общий UUID primary key + `created_at`/`updated_at`.
- `app/db/session.py` - `async_sessionmaker`, dependency `get_async_session`
  делает commit после request и rollback на exception.
- `app/db/base.py` импортирует модели для Alembic/relationship registration.
- Миграции в `backend/alembic/versions/`.

Routers:

- `auth.py` - register/login/refresh/logout.
- `users.py` - `/users/me`.
- `profiles.py` - профиль пользователя и список medical restrictions.
- `exercises.py` - каталог упражнений, мышцы, оборудование.
- `workouts.py` - генерация планов, активация/удаление, календарь, start,
  reschedule, complete, logging sets.
- `nutrition.py` - генерация питания, планы, поиск продуктов, логи еды,
  daily summary, распознавание еды по фото.
- `chat.py` - conversations + SSE streaming messages.
- `analytics.py` - вес, замеры, dashboard, прогресс упражнений, история.
- `files.py` - generic image upload.

Auth flow:

- Регистрация создает пользователя `is_verified=false`, создает одноразовый
  email verification token и отправляет письмо через SMTP.
- До подтверждения email backend не выдает access/refresh tokens.
- `/auth/verify-email` подтверждает token, выставляет `is_verified=true` и
  выдает access token в JSON + refresh token в HttpOnly cookie.
- Login/refresh/protected API блокируют неподтвержденных пользователей с
  кодом `EMAIL_NOT_VERIFIED`.
- Backend выдает access token в JSON и refresh token в HttpOnly cookie.
- Refresh token хранится в БД как SHA-256 hash, при refresh ротируется.
- Frontend хранит access token в Zustand memory, user persistится в localStorage.
- `frontend/src/app/api/auth/refresh/route.ts` проксирует refresh через backend,
  чтобы браузер мог обновить access token.
- Middleware смотрит только наличие `refresh_token` cookie и редиректит
  protected pages.

AI services:

- `app/services/ai/provider.py` выбирает провайдера. В режиме `auto`
  Anthropic имеет приоритет, если есть Anthropic key; OpenAI остается fallback,
  если Anthropic key не задан.
- `workout_generator.py` строит контекст пользователя, грузит все упражнения,
  просит AI provider вернуть JSON, валидирует `exercise_id`, сохраняет
  `WorkoutPlan -> WorkoutSession -> WorkoutExercise`.
- `nutrition_generator.py` требует профиль, считает BMR/TDEE/macros, просит
  AI provider JSON-план, создает `NutritionPlan -> Meal -> MealItem`, а
  отсутствующие продукты добавляет как `FoodItem(is_verified=False)`.
- `chat_engine.py` стримит ответ AI provider, добавляя последние 20 сообщений и
  профиль пользователя в system context.
- `food_recognizer.py` отправляет base64 image в vision provider и возвращает
  оценку продуктов/КБЖУ.
- Если ни один AI provider не настроен, workout/nutrition/chat/photo recognition
  используют deterministic fallback, чтобы MVP не падал во время локального демо.

Seed data:

- `seed_db.py` сидит мышцы, оборудование, мед. ограничения, упражнения, еду.
- Фактические счетчики по seed-файлам: 91 упражнение, 115 продуктов, 21 группа
  мышц, 20 типов оборудования, 15 medical restrictions.

## Data model overview

Пользователь:

- `User` имеет `profile`, `oauth_accounts`, `refresh_tokens`,
  `workout_plans`, `nutrition_plans`, `chat_conversations`.
- `OAuthAccount` модель есть, но OAuth routes не реализованы.

Профиль:

- `UserProfile` хранит персональные данные, цель, активность, оборудование,
  дни тренировок, питание, аллергии, disliked foods, health notes.
- Medical restrictions связаны через `UserMedicalRestriction`.

Тренировки:

- `WorkoutPlan` принадлежит user.
- `WorkoutSession` - шаблон дня внутри плана.
- `WorkoutExercise` - упражнение в конкретной сессии.
- `ScheduledWorkout` - конкретное событие календаря.
- `ExerciseSet` - залогированный подход, опционально связан с
  `ScheduledWorkout`.

Питание:

- `FoodItem` - справочник продуктов.
- `NutritionPlan`, `Meal`, `MealItem` - AI-план питания.
- `NutritionLog` - дневник фактически съеденного.

Аналитика:

- `WeightLog` - вес по датам.
- `MeasurementLog` - замеры тела по типам.
- Прогресс упражнений считается из `ExerciseSet`.

Чат:

- `ChatConversation` и `ChatMessage`.

## Frontend architecture

Маршруты:

- `/` - marketing page.
- `/login`, `/register` - email/password auth.
- `/verify-email` - ожидание письма, resend и подтверждение email token.
- `/onboarding` - пошаговое заполнение профиля.
- `/dashboard` - сводка.
- `/workouts` и `/workouts/[workoutId]` - планы, календарь, сессии, лог подходов.
- `/nutrition` - план питания, дневник еды, распознавание фото.
- `/chat` - чат с ИИ-тренером.
- `/exercises` - каталог упражнений с фильтрами.
- `/analytics` - вес, замеры, прогресс упражнений, история тренировок.
- `/profile` - просмотр профиля и logout.

Клиент API:

- `frontend/src/lib/api/client.ts` - общий `ky` client.
- API modules лежат в `frontend/src/lib/api/*.ts`.
- Query hooks лежат в `frontend/src/lib/queries/*.ts`.
- Типы API/UI лежат в `frontend/src/types/*.ts`.

Auth/UI state:

- `auth-store.ts` хранит `accessToken`, `user`, `isAuthenticated`; persist
  сохраняет только `user`.
- `ui-store.ts` хранит состояние sidebar.
- `DashboardLayout` проверяет полноту профиля и отправляет на `/onboarding`,
  если обязательные поля не заполнены.

Компоненты:

- `components/ui/` - shadcn-style primitives.
- `components/shared/` - общие карточки/заголовки/loading/empty.
- `components/three/` - `ExerciseViewer`, `ModelLoader`, `BodyModel`; сейчас
  не подключены к страницам, и в `public/` нет 3D model assets.

## Что уже сделано

Готово или в рабочем состоянии:

- Email/password регистрация и login.
- Строгая email verification через SMTP: без подтверждения нельзя попасть в
  onboarding/dashboard.
- Refresh token rotation через backend + Next refresh route.
- Онбординг и профиль пользователя с медицинскими ограничениями.
- Редактирование профиля идет через `/onboarding`; форма предзаполняется
  текущими данными профиля.
- Seed catalog: упражнения, мышцы, оборудование, продукты.
- Каталог упражнений с фильтрами и поиском.
- AI-генерация тренировочного плана.
- Активация/удаление workout plans.
- Календарь тренировок: auto-schedule, ручное добавление, перенос, удаление,
  toggle completion.
- Экран активной тренировки: подходы, вес/повторы, rest timer, finish workout.
- AI-чат со streaming response и историей диалога.
- AI-генерация плана питания.
- Дневник еды, daily summary, отображение active nutrition plan.
- Распознавание еды по фото через настроенный vision-capable AI provider.
- Аналитика веса, замеров, питания за текущий день, прогресса упражнений и
  истории завершенных сессий.
- Базовый production Docker/Nginx/Certbot setup.

## Что не готово или частично

- Тестовое покрытие почти отсутствует: есть только минимальный `unittest` для
  email verification token helpers, frontend test runner не настроен, CI нет.
- OAuth: модели и env Google/Яндекс/VK есть, но backend routes и frontend
  handlers не реализованы. Неработающие OAuth-кнопки в UI скрыты.
- Avatar/file upload: backend endpoint есть, frontend API wrapper есть, но UI не
  подключен.
- Uploaded files не раздаются: backend возвращает `/uploads/...`, но FastAPI не
  монтирует `StaticFiles`, а nginx не проксирует/не отдает `/uploads/`.
- 3D-визуализация подготовлена компонентами, но не используется и нет model
  assets.
- Redis/rate limiting не используются, хотя зависимость и compose есть.
- Password reset отсутствует; middleware считает `/reset-password`, `/privacy`,
  `/terms` публичными, но страниц нет.
- Logout удаляет cookie, но не отзывает refresh token в БД.
- Nutrition food search hook/API есть, но UI ручного добавления не использует
  поиск по справочнику.
- Нет delete/edit для food logs, workout sets, measurements/weight logs.
- Нет уведомлений/напоминаний и адаптивной корректировки нагрузки.

## Важные риски и баги

Высокий приоритет:

- `/uploads/...` сейчас не обслуживается, поэтому avatar/photo URLs не откроются.
- `POST /workouts/exercises/{workout_exercise_id}/log` не проверяет, что
  `WorkoutExercise` принадлежит текущему user. Нужно join через
  `WorkoutSession -> WorkoutPlan.user_id`.
- `analytics/dashboard` считает `workouts_this_week` и streak по `ExerciseSet`
  без фильтра по текущему user. Это может смешивать данные пользователей.

Средний приоритет:

- File upload доверяет `content_type`, не проверяет magic bytes/Pillow и
  принимает `folder` из формы как часть пути. Нужно ограничить folder allowlist
  и нормализовать путь.
- `nutrition/recognize` не ограничивает size/content type перед отправкой в
  OpenAI.
- README частично устарел: frontend фактически Next 16, питание/recognition уже
  реализованы, Docker/seed команды требуют корректировки.
- AI JSON parsing работает через `response_format={"type": "json_object"}`,
  но нет retry/repair и нет тестовых моков.

## Правила продолжения разработки

- При изменении API синхронизировать backend schemas и frontend `src/types` +
  `src/lib/api`.
- При изменении моделей БД создавать Alembic migration.
- Для ownership-sensitive endpoints всегда проверять принадлежность данных
  текущему `user.id` через join до записи/чтения.
- Для OpenAI-фич держать код тестируемым через мок клиента; реальные вызовы
  дорогие и зависят от ключа/сети.
- Перед изменениями frontend учитывать Next App Router route groups:
  `(marketing)`, `(auth)`, `(onboarding)`, `(dashboard)`.
- Для production env помнить различие:
  `NEXT_PUBLIC_API_URL` - публичная база для браузера,
  `BACKEND_URL` - внутренняя база для Next server route.

## Рекомендуемый следующий план

1. Подключить отдачу uploads или убрать URLs до готовой file-storage стратегии.
2. Закрыть ownership bugs в workout set logging и analytics dashboard.
3. Добавить минимальные backend tests для auth, workouts ownership, analytics
   scoping, nutrition logs.
4. Довести профиль: avatar upload, отдельный короткий edit UI без прохождения
   всех шагов onboarding, server-side file validation.
5. Реализовать OAuth или удалить неиспользуемые модели/env, если соцвход не
   нужен для MVP.
6. Подключить/удалить 3D-компоненты: сейчас они создают ожидание, но не дают
   пользовательской ценности.
7. Обновить README после исправления команд и статусов.

## Проверка 2026-05-18

Локально были подняты PostgreSQL/Redis, backend на `127.0.0.1:8000` и frontend
на `localhost:3000`. Через браузер и API проверены: регистрация/login,
onboarding, dashboard, workouts generate/activate/calendar/log set, nutrition
generate/log/photo recognition, chat fallback, exercises search/filter/reset,
analytics weight/measurements/workouts/history/nutrition, profile edit.

Исправлено по ходу проверки:

- `profiles/me` больше не падает на async lazy-load medical restrictions.
- Workout/nutrition/chat/photo AI-сервисы не падают без `OPENAI_API_KEY`.
- Кнопки activate/delete workout card не прерываются из-за вложенного link.
- Мобильный sidebar overlay и закрытые sheets больше не блокируют клики.
- Убраны мертвые OAuth-кнопки login/register.
- Analytics nutrition tab заменен с "Скоро" на рабочие показатели текущего дня.
- Workout session state переписан без setState-in-effect ошибок React Compiler.

Команды, которые прошли после правок:

```bash
cd frontend && npm run lint
cd frontend && npm run build
backend/.venv/bin/python -m compileall backend/app
```

## Проверка 2026-05-19

Добавлена строгая email verification:

- `POST /auth/register` создает аккаунт без сессии и отправляет verification
  email.
- `POST /auth/login` до подтверждения возвращает `EMAIL_NOT_VERIFIED`.
- `POST /auth/verify-email` подтверждает token, выставляет `is_verified=true`
  и выдает access/refresh tokens.
- `POST /auth/resend-verification` возвращает generic ответ без раскрытия,
  существует ли email.

Создана миграция `7f2c1d8a9b3e_add_email_verification_tokens.py`, добавлен
SMTP-сервис и route `/verify-email` на frontend. Локальная БД обновлена через
`alembic upgrade head`.

Команды/проверки, которые прошли:

```bash
DEBUG=false PYTHONPATH=backend backend/.venv/bin/python -m unittest backend.tests.test_email_verification_security
DEBUG=false backend/.venv/bin/python -m compileall backend/app
cd frontend && npm run lint
cd frontend && npm run build
```

API smoke-test:

- register вернул `200` и `requires_verification=true`.
- login до verify вернул `403 EMAIL_NOT_VERIFIED`.
- verify-email вернул `200`, `is_verified=true` и `Set-Cookie: refresh_token`.
- login после verify вернул `200`.
- invalid verify token вернул `400`.

Demo update 2026-05-19:

- Для демонстрации на `coach-ai.ru` выставлен `EMAIL_VERIFICATION_REQUIRED=false`.
- Новый register возвращает `requires_verification=false`, не отправляет письмо,
  login сразу возвращает access token, `user.is_verified=true`.

Email verification restored 2026-05-19:

- `EMAIL_VERIFICATION_REQUIRED=true` снова включен на `coach-ai.ru`.
- Gmail App Password проверен: локально SMTP login OK; на VPS из backend
  container прямой SMTP падал из-за IPv4 SMTP timeout.
- Добавлен `backend/scripts/smtp_tcp_proxy.py` и service `smtp-proxy` в
  `docker-compose.prod.yml`; после UFW allow для bridge backend SMTP login OK.
- Register на prod возвращает `requires_verification=true`; login до verify
  возвращает `403 EMAIL_NOT_VERIFIED`.
- При обязательной верификации backend теперь отправляет письмо строго: если
  email service падает, API возвращает `503 EMAIL_SERVICE_ERROR`, а frontend
  показывает ошибку вместо перехода на страницу кода.

Добавлен Anthropic provider без удаления OpenAI:

- `AI_PROVIDER=auto` предпочитает Anthropic, если задан Anthropic key.
- OpenAI остается доступен через `AI_PROVIDER=openai`.
- Поддержаны `ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY_2` и
  `ANTHROPIC_API_KEYS` через запятую.
- Workout, nutrition, chat streaming и food photo recognition теперь идут через
  общий `app/services/ai/provider.py`.
- 2026-05-19 оба Anthropic key проверены реальными минимальными вызовами:
  `claude-haiku-4-5-20251001` вернул `OK`; `claude-3-5-haiku-20241022` для этих
  ключей вернул `404 not_found_error`.

Дополнительные проверки:

```bash
DEBUG=false PYTHONPATH=backend backend/.venv/bin/python -m unittest backend.tests.test_ai_provider backend.tests.test_email_verification_security
DEBUG=false AI_PROVIDER=auto ANTHROPIC_API_KEY=sk-ant-test OPENAI_API_KEY=sk-openai-test PYTHONPATH=backend backend/.venv/bin/python - <<'PY'
from app.services.ai.provider import get_configured_ai_provider
print(get_configured_ai_provider())
PY
```

## Команды проверки

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Backend:

```bash
cd backend
python -m compileall app scripts
PYTHONPATH=. python -m unittest tests.test_email_verification_security
alembic current
```

Production smoke:

```bash
backend/.venv/bin/python scripts/prod_smoke.py --base-url https://coach-ai.ru
```

2026-05-19 полный production smoke прошел `23 passed, 0 failed`: auth,
frontend refresh proxy, profile, exercises, workouts, nutrition, analytics,
file upload/static serving, chat streaming/delete, OpenAPI/docs routing.
