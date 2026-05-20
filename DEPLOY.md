# Production Deploy

Домен: `coach-ai.ru`.

Проверено 2026-05-19: `coach-ai.ru` и `www.coach-ai.ru` ведут на VPS
`147.45.149.215`; HTTPS-сертификат Let's Encrypt выпущен до `2026-08-17`.

## 1. DNS

В панели RU-CENTER/NIC.RU укажите A-записи:

```text
coach-ai.ru      A  <VPS_IP>
www.coach-ai.ru  A  <VPS_IP>
```

TTL можно поставить 300-600 секунд на время запуска.

## 2. VPS

Минимум для MVP: 2 vCPU, 4 GB RAM, 30+ GB SSD, Ubuntu 24.04 LTS.

На сервере:

```bash
apt update && apt upgrade -y
apt install -y ca-certificates curl gnupg ufw fail2ban unattended-upgrades
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" \
  > /etc/apt/sources.list.d/docker.list
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
systemctl enable --now docker fail2ban
```

## 3. Local Production Env

На локальной машине:

```bash
cp .env.prod.example .env.prod
```

Заполните `.env.prod`: `DOMAIN`, `ADMIN_EMAIL`, `DB_*`, `SECRET_KEY`,
Anthropic/OpenAI ключи и SMTP. Файл не коммитится.

## 4. Deploy

```bash
scripts/deploy_vps.sh root@<VPS_IP> /opt/ai-trainer
```

После первого успешного запуска:

```bash
ssh root@<VPS_IP> 'cd /opt/ai-trainer && docker compose -f docker-compose.prod.yml ps'
curl -I https://coach-ai.ru
```

## 5. Certificate Renewal

На сервере добавьте cron:

```bash
(crontab -l 2>/dev/null; echo '15 4 * * * cd /opt/ai-trainer && scripts/renew_certs.sh >/var/log/ai-trainer-certbot.log 2>&1') | crontab -
```
