#!/bin/bash
set -e

echo "🔐 Настройка HTTPS для KKT System (Webroot метод)"
echo "=========================================="

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
DOMAIN="kkt-box.net"
EMAIL="master@relabs.center"
WEBROOT="/var/www/html"

echo -e "${YELLOW}ШАГ 1: Установка Certbot${NC}"
if ! command -v certbot &> /dev/null; then
    echo "📦 Установка Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
else
    echo "✅ Certbot уже установлен"
fi

echo ""
echo -e "${YELLOW}ШАГ 2: Проверка DNS конфигурации${NC}"
RESOLVED_IP=$(dig +short $DOMAIN | tail -n1)
echo "📍 Домен $DOMAIN резолвится в: $RESOLVED_IP"
echo "📍 IP сервера: $(curl -s ifconfig.me)"

echo ""
echo -e "${YELLOW}ШАГ 3: Подготовка директории webroot${NC}"
mkdir -p $WEBROOT/.well-known/acme-challenge
chmod -R 755 $WEBROOT/.well-known
echo "✅ Директория $WEBROOT/.well-known/acme-challenge готова"

echo ""
echo -e "${YELLOW}ШАГ 4: Остановка Docker контейнера task_tracker_web${NC}"
if docker ps | grep -q 'task_tracker_web'; then
    echo "⚠️  Найден контейнер task_tracker_web на порту 80"
    echo "🛑 Останавливаем task_tracker_web..."
    docker stop task_tracker_web
    echo "✅ task_tracker_web остановлен"
else
    echo "ℹ️  task_tracker_web уже остановлен"
fi

echo ""
echo -e "${YELLOW}ШАГ 5: Настройка временной конфигурации Nginx${NC}"

# Создаём временную конфигурацию для получения сертификата
cat > /etc/nginx/sites-available/kkt-system << 'EOF'
server {
    listen 80;
    server_name kkt-box.net www.kkt-box.net 185.185.71.248;
    
    # Для Let's Encrypt validation - ПРИОРИТЕТ!
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/html;
        default_type text/plain;
        allow all;
        try_files $uri =404;
    }
    
    # Все остальные запросы на приложение
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "✅ Временная конфигурация создана"

echo ""
echo -e "${YELLOW}ШАГ 6: Перезагрузка Nginx${NC}"
nginx -t
if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo "✅ Nginx перезагружен"
else
    echo -e "${RED}❌ Ошибка конфигурации Nginx${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}ШАГ 7: Тест доступности webroot${NC}"
TEST_FILE="$WEBROOT/.well-known/acme-challenge/test-$(date +%s).txt"
echo "test-content" > $TEST_FILE
sleep 1

TEST_URL="http://$DOMAIN/.well-known/acme-challenge/$(basename $TEST_FILE)"
echo "🧪 Тестирую: $TEST_URL"
RESPONSE=$(curl -s -w "\n%{http_code}" $TEST_URL)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
CONTENT=$(echo "$RESPONSE" | head -n1)

if [ "$HTTP_CODE" == "200" ] && [ "$CONTENT" == "test-content" ]; then
    echo -e "${GREEN}✅ Webroot доступен и работает корректно${NC}"
    rm -f $TEST_FILE
else
    echo -e "${RED}❌ ОШИБКА: Webroot недоступен${NC}"
    echo "HTTP Code: $HTTP_CODE"
    echo "Content: $CONTENT"
    exit 1
fi

echo ""
echo -e "${YELLOW}ШАГ 8: Получение SSL сертификата (Webroot метод)${NC}"
echo "🔐 Запуск Certbot с webroot методом..."

# Удаляем старые попытки если есть
certbot delete --cert-name $DOMAIN --non-interactive 2>/dev/null || true

# Получаем сертификат используя webroot
if certbot certonly \
    --webroot \
    -w $WEBROOT \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --no-eff-email \
    --verbose; then
    echo -e "${GREEN}✅ Сертификат успешно получен!${NC}"
else
    echo -e "${RED}❌ Ошибка получения сертификата${NC}"
    echo "Проверьте логи: /var/log/letsencrypt/letsencrypt.log"
    # Запускаем Docker обратно
    docker start task_tracker_web 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${YELLOW}ШАГ 9: Настройка финальной конфигурации Nginx с HTTPS${NC}"

# Создаём финальную конфигурацию с HTTPS
cat > /etc/nginx/sites-available/kkt-system << 'EOF'
# Редирект с HTTP на HTTPS
server {
    listen 80;
    server_name kkt-box.net www.kkt-box.net 185.185.71.248;
    
    # Для обновления сертификата
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
    
    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/kkt-box.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kkt-box.net/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Заголовки безопасности
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    client_max_body_size 100M;
    
    # API endpoint для восстановления БД с увеличенным таймаутом
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
    
    # Остальные API endpoints
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
    
    # Статические файлы
    location /static/ {
        alias /home/kktapp/kkt-system/web/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Корень и HTML страницы
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP сервер для IP адреса (без HTTPS)
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

echo "✅ Финальная конфигурация создана"

echo ""
echo -e "${YELLOW}ШАГ 10: Проверка и перезагрузка Nginx${NC}"
nginx -t
if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo -e "${GREEN}✅ Nginx перезагружен с HTTPS конфигурацией${NC}"
else
    echo -e "${RED}❌ Ошибка конфигурации Nginx${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}ШАГ 11: Запуск Docker контейнера обратно${NC}"
echo "🐳 Запуск task_tracker_web..."
# Не запускаем обратно - теперь Nginx на порту 80
echo "ℹ️  task_tracker_web остаётся остановленным (порт 80 занят Nginx)"
echo "ℹ️  Для доступа к task_tracker используйте порт 3000 напрямую"

echo ""
echo -e "${YELLOW}ШАГ 12: Настройка автообновления сертификата${NC}"
if certbot renew --dry-run; then
    echo -e "${GREEN}✅ Автообновление сертификата проверено${NC}"
else
    echo -e "${YELLOW}⚠️  Проверьте настройку автообновления${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 HTTPS успешно настроен!${NC}"
echo ""
echo "📋 Информация:"
echo "   Домен HTTPS: https://$DOMAIN"
echo "   Домен HTTP: http://185.185.71.248:8000"
echo "   Сертификат: Let's Encrypt"
echo "   Срок действия: 90 дней (автообновление)"
echo ""
echo "🔍 Тесты:"
echo "   curl -I https://$DOMAIN"
echo "   curl -I http://$DOMAIN (должен редиректить на HTTPS)"
echo ""
echo "📄 Информация о сертификате:"
certbot certificates
echo ""
echo "⚠️  ВАЖНО: task_tracker_web остановлен"
echo "   Для доступа используйте: http://185.185.71.248:3000"
echo "   Или настройте отдельный поддомен для него"
echo ""
echo "=========================================="
