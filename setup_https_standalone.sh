#!/bin/bash
set -e

echo "🔐 Настройка HTTPS для KKT System (Standalone режим)"
echo "=========================================="

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
DOMAIN="kkt-box.net"
EMAIL="master@relabs.center"

echo -e "${YELLOW}ШАГ 1: Установка Certbot${NC}"
if ! command -v certbot &> /dev/null; then
    echo "📦 Установка Certbot..."
    apt-get update
    apt-get install -y certbot
else
    echo "✅ Certbot уже установлен"
fi

echo ""
echo -e "${YELLOW}ШАГ 2: Проверка DNS конфигурации${NC}"
RESOLVED_IP=$(dig +short $DOMAIN | tail -n1)
echo "📍 Домен $DOMAIN резолвится в: $RESOLVED_IP"
echo "📍 IP сервера: $(curl -s ifconfig.me)"

echo ""
echo -e "${YELLOW}ШАГ 3: Остановка служб для получения сертификата${NC}"

# Останавливаем Nginx
systemctl stop nginx || true

# Останавливаем KKT приложение
systemctl stop kkt-web.service || true

# ВАЖНО: Останавливаем Docker контейнер task_tracker_web который занимает порт 80
echo "🐳 Проверка Docker контейнеров на порту 80..."
if docker ps | grep -q 'task_tracker_web'; then
    echo "⚠️  Найден контейнер task_tracker_web на порту 80"
    echo "🛑 Останавливаем task_tracker_web..."
    docker stop task_tracker_web
    echo "✅ task_tracker_web остановлен"
fi

sleep 2

# Проверяем что порт 80 свободен
if lsof -i :80 > /dev/null 2>&1; then
    echo -e "${RED}❌ ОШИБКА: Порт 80 всё ещё занят!${NC}"
    lsof -i :80
    exit 1
fi

echo "✅ Порт 80 свободен"

echo ""
echo -e "${YELLOW}ШАГ 4: Получение SSL сертификата (Standalone режим)${NC}"
echo "🔐 Запуск Certbot в standalone режиме..."

# Удаляем старые попытки если есть
certbot delete --cert-name $DOMAIN --non-interactive 2>/dev/null || true

# Получаем сертификат
if certbot certonly \
    --standalone \
    --preferred-challenges http \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --no-eff-email; then
    echo -e "${GREEN}✅ Сертификат успешно получен!${NC}"
else
    echo -e "${RED}❌ Ошибка получения сертификата${NC}"
    echo "Запуск служб обратно..."
    systemctl start kkt-web.service
    systemctl start nginx
    # Запускаем Docker обратно
    docker start task_tracker_web 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${YELLOW}ШАГ 5: Настройка Nginx для HTTPS${NC}"

# Создаём финальную конфигурацию с HTTPS
cat > /etc/nginx/sites-available/kkt-system << 'EOF'
# Редирект с HTTP на HTTPS
server {
    listen 80;
    server_name kkt-box.net www.kkt-box.net 185.185.71.248;
    
    # Для обновления сертификата - ДОЛЖНО БЫТЬ ПЕРВЫМ!
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/html;
        default_type text/plain;
        allow all;
    }
    
    # Редирект на HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# Основной HTTPS сервер
server {
    listen 443 ssl http2;
    server_name kkt-box.net www.kkt-box.net;
    
    # SSL сертификаты (управляются Certbot)
    ssl_certificate /etc/letsencrypt/live/kkt-box.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kkt-box.net/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Безопасность
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    client_max_body_size 100M;
    
    # API endpoints with special timeout for database restore
    location /api/database/restore {
        proxy_pass http://localhost:8000;
        proxy_connect_timeout 180s;
        proxy_send_timeout 180s;
        proxy_read_timeout 180s;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API endpoints with normal timeout
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static/ {
        alias /home/kktapp/kkt-system/web/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Root and HTML pages
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTPS для IP адреса (без сертификата)
server {
    listen 80;
    server_name 185.185.71.248;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "✅ Конфигурация Nginx создана"

echo ""
echo -e "${YELLOW}ШАГ 6: Проверка конфигурации Nginx${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Конфигурация Nginx валидна${NC}"
else
    echo -e "${RED}❌ Ошибка в конфигурации Nginx${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}ШАГ 7: Запуск служб${NC}"
systemctl start kkt-web.service
systemctl start nginx

# Запускаем Docker контейнер обратно
echo "🐳 Запуск task_tracker_web..."
docker start task_tracker_web 2>/dev/null || echo "⚠️  task_tracker_web не нужен запуск"

# Проверяем статус
sleep 2
if systemctl is-active --quiet nginx && systemctl is-active --quiet kkt-web.service; then
    echo -e "${GREEN}✅ Все службы запущены${NC}"
else
    echo -e "${RED}❌ Ошибка запуска служб${NC}"
    systemctl status nginx --no-pager
    systemctl status kkt-web.service --no-pager
    exit 1
fi

echo ""
echo -e "${YELLOW}ШАГ 8: Настройка автообновления сертификата${NC}"
# Certbot автоматически создаёт cron job для обновления
if certbot renew --dry-run; then
    echo -e "${GREEN}✅ Автообновление сертификата настроено${NC}"
else
    echo -e "${YELLOW}⚠️  Проверьте настройку автообновления${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 HTTPS успешно настроен!${NC}"
echo ""
echo "📋 Информация:"
echo "   Домен: https://$DOMAIN"
echo "   Сертификат: Let's Encrypt"
echo "   Срок действия: 90 дней (автообновление)"
echo ""
echo "🔍 Тест:"
echo "   curl -I https://$DOMAIN"
echo ""
echo "📄 Сертификаты:"
certbot certificates
echo ""
echo "=========================================="
