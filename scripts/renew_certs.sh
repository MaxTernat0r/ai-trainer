#!/usr/bin/env bash
set -Eeuo pipefail

docker compose -f docker-compose.prod.yml run --rm --entrypoint certbot certbot \
  renew --webroot -w /var/www/certbot --quiet
docker compose -f docker-compose.prod.yml restart nginx
