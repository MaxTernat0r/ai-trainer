# AI Trainer — Claude Project Context

Дата составления: 2026-05-20. Этот файл — рабочая память для Claude Code. Не дублирует README; фиксирует фактическое состояние, инфраструктуру и подводные камни. Для исторического контекста см. `CODEX.md`, для деплоя — `DEPLOY.md`.

## TL;DR

- Монорепозиторий: `backend/` (FastAPI + async SQLAlchemy + Postgres), `frontend/` (Next.js 16 App Router), `nginx/`, `docker-compose.prod.yml`.
- Production: VPS `147.45.149.215`, домен `coach-ai.ru` (+ `www.`), HTTPS Let's Encrypt до `2026-08-17`. Деплой через `scripts/deploy_vps.sh root@<VPS_IP> /opt/ai-trainer`.
- Email verification ВКЛЮЧЕНА на проде (`EMAIL_VERIFICATION_REQUIRED=true`). Без подтверждения — `403 EMAIL_NOT_VERIFIED`.
- AI: `AI_PROVIDER=auto` — Anthropic в приоритете (`claude-haiku-4-5-20251001`), OpenAI fallback. Если ни один не настроен — детерминированные fallback-ответы.
- Текущая ветка: `main`. Рабочее дерево грязное (много модифицированных файлов после последнего коммита `da3ab05`).

## Структура

```
ai-trainer/
├── backend/                # FastAPI app
│   ├── app/
│   │   ├── core/           # config, security, exceptions
│   │   ├── db/             # base_model, session
│   │   ├── models/         # SQLAlchemy: user, profile, exercise, workout, nutrition, chat, analytics
│   │   ├── routers/        # auth, users, profiles, exercises, workouts, nutrition, chat, analytics, files
│   │   ├── schemas/        # Pydantic
│   │   ├── services/
│   │   │   ├── ai/         # provider, openai_client, workout/nutrition/chat/food_recognizer
│   │   │   └── email.py    # Brevo / Resend / SMTP
│   │   ├── seeds/
│   │   └── main.py         # create_app(), CORS, mount /uploads
│   ├── alembic/versions/   # 8 миграций
│   ├── scripts/seed_db.py  # !!! НЕ app.scripts.seed_db — запускать как `python -m scripts.seed_db` из backend/
│   ├── scripts/smtp_tcp_proxy.py
│   ├── tests/              # pytest, есть unittest-ы
│   └── Dockerfile
├── frontend/               # Next.js 16.1.6 App Router, output: standalone
│   ├── src/
│   │   ├── app/
│   │   │   ├── (marketing)/    # /
│   │   │   ├── (auth)/         # /login, /register, /verify-email
│   │   │   ├── (onboarding)/   # /onboarding
│   │   │   ├── (dashboard)/    # /dashboard, /workouts, /nutrition, /chat, /exercises, /analytics, /profile
│   │   │   └── api/auth/refresh/route.ts  # Next-side refresh proxy → backend
│   │   ├── components/{ui, shared, three, auth}/
│   │   └── lib/{api, queries, hooks, stores, providers}/
│   └── Dockerfile
├── nginx/
│   ├── nginx.conf              # prod, HTTPS, маршрутизация на backend/frontend
│   └── nginx-bootstrap.conf    # HTTP-only для первого certbot-запуска
├── scripts/
│   ├── deploy_vps.sh           # rsync + docker compose up на VPS
│   ├── renew_certs.sh          # certbot renew + nginx reload
│   └── prod_smoke.py           # production smoke-тесты (23 кейса)
├── docker-compose.prod.yml
├── docker-compose.bootstrap.yml
└── backend/docker-compose.yml  # локальный db+redis+app
```

## Стек (по факту)

**Backend** — Python 3.12, FastAPI 0.115, async SQLAlchemy 2 + asyncpg + Postgres 16, Alembic, JWT (python-jose) + bcrypt/passlib, Pillow, httpx[socks], OpenAI SDK, Anthropic через httpx (не SDK), pydantic-settings.

**Frontend** — Next.js 16.1.6, React 19.2.3, TypeScript strict, Tailwind 4, shadcn/Radix UI, TanStack Query v5, Zustand (auth, ui), ky, Recharts, react-hook-form + zod, lucide-react, framer-motion. Three.js/R3F есть, но **в страницах не используются** и моделей в `public/` нет.

**Инфра** — Docker Compose, nginx, Let's Encrypt (certbot webroot), Redis (объявлен в compose, но rate limiting / cache **не подключены в коде**).

## Запуск локально

Backend:
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env  # опционально, settings читает и ../.env, и ./.env
alembic upgrade head
python -m scripts.seed_db        # ВАЖНО: не app.scripts (README устарел)
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend && npm install && npm run dev   # http://localhost:3000
```

DB+Redis локально через compose:
```bash
cd backend && docker compose up -d db redis
```

## Production деплой

Production-окружение задаётся `.env.prod` (не коммитится). Шаблон — `.env.prod.example`.

Деплой целиком:
```bash
scripts/deploy_vps.sh root@<VPS_IP> /opt/ai-trainer
```

Что делает скрипт:
1. `rsync` репо на VPS (с исключением .git, .env, node_modules, .next, .venv, certs, uploads).
2. Заливает `.env.prod` как `.env` на сервер, `chmod 600`.
3. `docker compose -f docker-compose.prod.yml build`.
4. Поднимает `db`+`redis`, ждёт `pg_isready`.
5. `alembic upgrade head` и `python -m scripts.seed_db` через одноразовый backend-контейнер.
6. Поднимает backend+frontend.
7. Если нет `nginx/certs/live/$DOMAIN/fullchain.pem` — поднимает bootstrap nginx (HTTP) и запускает certbot. Иначе сразу полный nginx.
8. `--force-recreate nginx`.

Альтернативный режим: `SKIP_CERTBOT=1 scripts/deploy_vps.sh ...` — поднять только bootstrap nginx (если ещё нет DNS/сертификата).

Проверка статуса на сервере:
```bash
ssh root@<VPS_IP> 'cd /opt/ai-trainer && docker compose -f docker-compose.prod.yml ps'
curl -I https://coach-ai.ru
```

Production smoke-тест локально (бьёт по проду):
```bash
backend/.venv/bin/python scripts/prod_smoke.py --base-url https://coach-ai.ru
```

Renew сертификата:
```bash
# на сервере, в crontab:
15 4 * * * cd /opt/ai-trainer && scripts/renew_certs.sh >/var/log/ai-trainer-certbot.log 2>&1
```

## Production compose сервисы

- **db** — postgres:16-alpine, volume `pgdata`.
- **redis** — redis:7-alpine.
- **backend** — собирается из `./backend`, env через `.env`, монтирует `./backend/uploads:/app/uploads`. Зависит от db, redis, smtp-proxy.
- **smtp-proxy** — собран из того же образа, `network_mode: host`, запускает `python -m scripts.smtp_tcp_proxy`. Слушает на `172.18.0.1:2525`, форвардит на `smtp.gmail.com:587` по IPv6 (костыль для Timeweb VPS — IPv4 SMTP залочен).
- **frontend** — `./frontend`, build-arg `NEXT_PUBLIC_API_URL=https://${DOMAIN}`, runtime `BACKEND_URL=http://backend:8000`. `output: standalone` → запускается как `node server.js`.
- **nginx** — alpine, порты 80/443. Конфиг `nginx/nginx.conf` (или `nginx-bootstrap.conf` через `docker-compose.bootstrap.yml`). Маршрутизация:
  - `= /api/auth/refresh` → frontend (Next refresh proxy)
  - `/openapi.json`, `/docs`, `/redoc`, `/uploads/`, `/api/` → backend
  - `/` → frontend
  - WebSocket upgrade на `/`
- **certbot** — webroot `/var/www/certbot`, выпускает на `${DOMAIN}` и `www.${DOMAIN}`.

## Email доставка

`EMAIL_PROVIDER=auto` пробует Brevo → Resend → SMTP. Рекомендация — HTTPS API (Brevo/Resend), потому что VPS-провайдеры часто режут исходящий SMTP.

SMTP на проде через `smtp-proxy` host-network контейнер (см. выше). Backend подключается к `SMTP_HOST=172.18.0.1`, `SMTP_PORT=2525`, но проверяет TLS hostname `smtp.gmail.com` через `SMTP_TLS_SERVER_HOSTNAME`. Gmail требует App Password.

UFW на VPS должен разрешать только `172.18.0.0/16 → 172.18.0.1:2525`.

При `EMAIL_VERIFICATION_REQUIRED=true` и падении email-сервиса register отдаёт `503 EMAIL_SERVICE_ERROR` — frontend показывает ошибку, а не уводит на страницу ввода кода.

## Auth flow

1. `POST /api/v1/auth/register` — создаёт `User(is_verified=false)`, генерирует email verification token, шлёт письмо. Возвращает `requires_verification`.
2. `POST /api/v1/auth/login` до verify → `403 EMAIL_NOT_VERIFIED`.
3. `POST /api/v1/auth/verify-email` — подтверждает token, ставит `is_verified=true`, возвращает access token (JSON) и refresh token (HttpOnly cookie).
4. `POST /api/v1/auth/refresh` — ротация refresh token (хранится как SHA-256 hash в БД).
5. `frontend/src/app/api/auth/refresh/route.ts` — Next.js маршрут-проксик, чтобы браузер мог рефрешить (cookie SameSite=strict).
6. Logout удаляет cookie, **но не отзывает refresh token в БД** (известная дыра).

Frontend хранит access token в Zustand (in-memory), `user` персистится в localStorage. Middleware смотрит наличие `refresh_token` cookie для protected pages.

## AI services

- `app/services/ai/provider.py` — выбор провайдера. `auto` → Anthropic если есть `ANTHROPIC_API_KEY*`, иначе OpenAI. Поддерживается несколько Anthropic-ключей: `ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY_2`, `ANTHROPIC_API_KEYS` (через запятую).
- `workout_generator.py` — собирает контекст (профиль + все упражнения из БД), просит JSON, валидирует `exercise_id`, сохраняет `WorkoutPlan → WorkoutSession → WorkoutExercise`.
- `nutrition_generator.py` — BMR/TDEE/macros, JSON-план, `NutritionPlan → Meal → MealItem`. Незнакомые продукты добавляет в `FoodItem(is_verified=False)`.
- `chat_engine.py` — SSE стриминг, добавляет последние 20 сообщений + профиль в system context.
- `food_recognizer.py` — vision (base64), оценка КБЖУ.
- Без AI ключей — детерминированный fallback, чтобы демо не падало.
- OpenAI поддерживает SOCKS5 через `OPENAI_PROXY_URL` (есть `socksio` в зависимостях).

Модели по умолчанию (актуально на 2026-05-19):
- Anthropic: `claude-haiku-4-5-20251001` (проверена на обоих ключах). `claude-3-5-haiku-20241022` для этих ключей возвращает 404.
- OpenAI: `gpt-5.4-mini`.

## Data model (быстрая шпаргалка)

- **User** — `profile`, `oauth_accounts` (модели есть, routes нет), `refresh_tokens`, `workout_plans`, `nutrition_plans`, `chat_conversations`.
- **UserProfile** — физ. параметры, цель, оборудование, дни тренировок, питание, аллергии, disliked_foods, health notes. Связь с `MedicalRestriction` через `UserMedicalRestriction`.
- **WorkoutPlan → WorkoutSession → WorkoutExercise** + `ScheduledWorkout` (события календаря) + `ExerciseSet` (логи подходов).
- **FoodItem** (справочник), **NutritionPlan → Meal → MealItem**, **NutritionLog**.
- **WeightLog**, **MeasurementLog**.
- **ChatConversation → ChatMessage**.

UUID PK, `created_at`/`updated_at` в `app/db/base_model.py`.

## Frontend routes

- `/` — лендинг.
- `/login`, `/register`, `/verify-email`.
- `/onboarding` — пошаговая форма; используется и для редактирования профиля.
- `/dashboard` — сводка. `DashboardLayout` редиректит на `/onboarding`, если профиль неполный.
- `/workouts`, `/workouts/[workoutId]` — планы, календарь, активная сессия.
- `/nutrition` — план, дневник, распознавание фото.
- `/chat`, `/exercises`, `/analytics`, `/profile`.

API-клиент — `frontend/src/lib/api/client.ts` (ky). Hooks — `frontend/src/lib/queries/*`.

## Что готово

См. `CODEX.md` детально. Кратко: auth + email verify, онбординг, AI-генерация workout/nutrition, календарь и сессии тренировок, чат-стриминг, food photo recognition, аналитика (вес, замеры, прогресс упражнений, история), exercises каталог, prod Docker/Nginx/Certbot.

## Известные проблемы и риски

**Высокий приоритет:**
- `POST /workouts/exercises/{id}/log` не проверяет ownership (`WorkoutSession → WorkoutPlan.user_id`).
- `analytics/dashboard` считает `workouts_this_week` и streak без фильтра по user.
- Logout не отзывает refresh token в БД.

**Средний приоритет:**
- File upload доверяет `content_type`, не валидирует magic bytes/Pillow и принимает `folder` из формы. Нужен allowlist + нормализация пути.
- `nutrition/recognize` не ограничивает size перед отправкой в OpenAI.
- AI JSON parsing без retry/repair.
- Avatar/file upload UI не подключён (backend есть).
- README частично устарел (Next 15 → 16, питание уже есть, команды seed).

**Не реализовано:**
- OAuth (Google/Yandex/VK) — модели и env есть, routes нет. UI-кнопки скрыты.
- Password reset (middleware пускает на `/reset-password`, страницы нет).
- 3D-визуализация (компоненты есть, моделей нет, страницы не используют).
- Redis rate limiting / cache.
- Уведомления, адаптивная нагрузка, тесты frontend, CI.

## Команды проверки

Frontend:
```bash
cd frontend && npm run lint && npm run build
```

Backend:
```bash
cd backend
python -m compileall app scripts
PYTHONPATH=. python -m unittest tests.test_email_verification_security
PYTHONPATH=. python -m unittest tests.test_ai_provider
alembic current
```

Production smoke:
```bash
backend/.venv/bin/python scripts/prod_smoke.py --base-url https://coach-ai.ru
```

## Подводные камни

- **Не пиши `python -m app.scripts.seed_db`** — скрипт лежит в `backend/scripts/seed_db.py`, запускать как `python -m scripts.seed_db` из `backend/`. README здесь врёт.
- **`.env.prod` не коммитится**, `.env` тоже. Settings читают `../.env` и `.env` относительно `backend/`.
- **`COOKIE_SAMESITE=strict`** на проде — refresh идёт через Next-side route same-origin, иначе cookie не пойдёт.
- **`NEXT_PUBLIC_API_URL` vs `BACKEND_URL`**: первое — публичная база для браузера, второе — внутреннее имя для Next server-side.
- **Build args**: `NEXT_PUBLIC_API_URL` зашивается в frontend на этапе build (Next baking), пересобирать при смене домена.
- **uploads** — каталог монтируется томом, FastAPI монтирует `/uploads` через StaticFiles, nginx тоже проксирует. UID контейнера `10001:10001`, `deploy_vps.sh` chown'ит.
- **При изменении API**: синхронизировать backend schemas ↔ `frontend/src/types` ↔ `frontend/src/lib/api`.
- **При изменении моделей**: создать Alembic миграцию.
- **Ownership-sensitive endpoints**: всегда join до `user.id`.

## Полезные ссылки

- Production: https://coach-ai.ru
- Repo: https://github.com/MaxTernat0r/ai-trainer
- VPS: `147.45.149.215` (Timeweb, Ubuntu 24.04)
- Domain registrar: RU-CENTER/NIC.RU
