#!/usr/bin/env bash
set -Eeuo pipefail

REMOTE="${1:-}"
REMOTE_DIR="${2:-/opt/ai-trainer}"
SSH_ARGS=()
if [[ -n "${SSH_OPTS:-}" ]]; then
  # Intentionally split SSH_OPTS into ssh arguments, for example:
  # SSH_OPTS="-o PubkeyAuthentication=no -o PreferredAuthentications=password"
  SSH_ARGS=(${SSH_OPTS})
fi
RSYNC_SSH="${RSYNC_SSH:-ssh ${SSH_OPTS:-}}"

if [[ -z "$REMOTE" ]]; then
  echo "Usage: scripts/deploy_vps.sh <ssh-host> [remote-dir]" >&2
  echo "Example: scripts/deploy_vps.sh deploy@203.0.113.10 /opt/ai-trainer" >&2
  exit 2
fi

if [[ ! -f .env.prod ]]; then
  echo "Missing .env.prod. Copy .env.prod.example to .env.prod and fill production values." >&2
  exit 2
fi

chmod 600 .env.prod

ssh ${SSH_ARGS[@]+"${SSH_ARGS[@]}"} "$REMOTE" "mkdir -p '$REMOTE_DIR'"

rsync -az --delete \
  -e "$RSYNC_SSH" \
  --exclude '.git/' \
  --exclude '.env' \
  --exclude '.env.prod' \
  --exclude '.venv/' \
  --exclude 'node_modules/' \
  --exclude '.next/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude 'nginx/certs/' \
  --exclude 'backend/uploads/*' \
  ./ "$REMOTE:$REMOTE_DIR/"

rsync -az -e "$RSYNC_SSH" .env.prod "$REMOTE:$REMOTE_DIR/.env"

ssh ${SSH_ARGS[@]+"${SSH_ARGS[@]}"} "$REMOTE" "REMOTE_DIR='$REMOTE_DIR' bash -s" <<'REMOTE_SCRIPT'
set -Eeuo pipefail

cd "$REMOTE_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed on the server. Install Docker Engine + Compose plugin first." >&2
  exit 3
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin is not available on the server." >&2
  exit 3
fi

env_get() {
  awk -F= -v key="$1" '$1 == key { sub(/^[^=]*=/, ""); print; exit }' .env
}

DOMAIN="$(env_get DOMAIN)"
ADMIN_EMAIL="$(env_get ADMIN_EMAIL)"
DB_USER="$(env_get DB_USER)"
DB_NAME="$(env_get DB_NAME)"

if [[ -z "${DOMAIN:-}" || -z "${ADMIN_EMAIL:-}" ]]; then
  echo "DOMAIN and ADMIN_EMAIL must be set in .env" >&2
  exit 4
fi

if [[ -z "${DB_USER:-}" || -z "${DB_NAME:-}" ]]; then
  echo "DB_USER and DB_NAME must be set in .env" >&2
  exit 4
fi

chmod 600 .env
mkdir -p nginx/certs backend/uploads
if command -v sudo >/dev/null 2>&1; then
  sudo chown -R 10001:10001 backend/uploads || true
else
  chown -R 10001:10001 backend/uploads || true
fi

docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d db redis

for attempt in $(seq 1 30); do
  if docker compose -f docker-compose.prod.yml exec -T db pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    break
  fi
  if [[ "$attempt" == "30" ]]; then
    echo "PostgreSQL did not become ready in time" >&2
    exit 5
  fi
  sleep 2
done

docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
docker compose -f docker-compose.prod.yml run --rm backend python -m scripts.seed_db
# Force-recreate sometimes keeps the old image if the `latest` tag was rebuilt;
# explicit stop+rm guarantees the new image is used. Stop nginx first because
# it depends on frontend/backend.
docker compose -f docker-compose.prod.yml stop nginx || true
for svc in backend frontend smtp-proxy; do
  docker compose -f docker-compose.prod.yml rm -sf "$svc" || true
done
docker compose -f docker-compose.prod.yml up -d backend frontend smtp-proxy

if [[ "${SKIP_CERTBOT:-0}" == "1" ]]; then
  docker compose -f docker-compose.prod.yml -f docker-compose.bootstrap.yml up -d --force-recreate nginx
  docker compose -f docker-compose.prod.yml ps
  echo "SKIP_CERTBOT=1: app is running behind HTTP bootstrap nginx. Update DNS, then rerun without SKIP_CERTBOT."
  exit 0
fi

if [[ ! -f "nginx/certs/live/$DOMAIN/fullchain.pem" ]]; then
  docker compose -f docker-compose.prod.yml -f docker-compose.bootstrap.yml up -d nginx
  docker compose -f docker-compose.prod.yml run --rm certbot
fi

docker compose -f docker-compose.prod.yml rm -sf nginx >/dev/null 2>&1 || true
docker compose -f docker-compose.prod.yml up -d nginx
docker compose -f docker-compose.prod.yml ps
REMOTE_SCRIPT

DOMAIN="$(awk -F= '$1 == "DOMAIN" { sub(/^[^=]*=/, ""); print; exit }' .env.prod)"
echo "Deploy finished. Check: https://${DOMAIN}"
