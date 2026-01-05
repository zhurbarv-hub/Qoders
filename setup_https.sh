#!/bin/bash
# Скрипт настройки HTTPS с Let's Encrypt для проекта ККТ

set -e  # Остановка при ошибке

echo "=== Установка HTTPS для KKT System ==="
echo ""

# Шаг 1: Установка Certbot
echo "📦 [1/5] Установка Certbot..."
apt-get update -qq
apt-get install -y certbot python3-certbot-nginx

# Шаг 2: Проверка DNS
echo ""
echo "🌐 [2/5] Проверка DNS для kkt-box.net..."
DOMAIN="kkt-box.net"
DNS_IP=$(dig +short $DOMAIN A | tail -n1)  # Только IPv4
SERVER_IP="185.185.71.248"  # Известный IP

echo "  Домен: $DOMAIN"
echo "  DNS указывает на: $DNS_IP"
echo "  IP сервера: $SERVER_IP"

if [ "$DNS_IP" != "$SERVER_IP" ]; then
    echo ""
    echo "⚠️  ВНИМАНИЕ: DNS записи не совпадают!"
    echo "   DNS: $DNS_IP, Сервер: $SERVER_IP"
    echo "   Продолжаем установку (Certbot справится с проверкой)..."
    echo ""
else
    echo "✅ DNS настроен правильно"
fi

# Шаг 3: Создание базовой конфигурации nginx для проверки
echo ""
echo "📝 [3/5] Подготовка Nginx конфигурации..."

# Резервная копия текущей конфигурации
cp /etc/nginx/sites-available/kkt-system /etc/nginx/sites-available/kkt-system.backup.before-https

# Временная конфигурация для получения сертификата
cat > /etc/nginx/sites-available/kkt-system << 'EOF'
server {
    listen 80;
    server_name kkt-box.net www.kkt-box.net 185.185.71.248;
    
    # Для проверки Let's Encrypt - ДОЛЖНО БЫТЬ ПЕРВЫМ!
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/html;
        default_type text/plain;
        allow all;
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

# Проверка и перезагрузка nginx
nginx -t && systemctl reload nginx
echo "✅ Nginx настроен для получения сертификата"

# Шаг 4: Получение SSL сертификата
echo ""
echo "🔐 [4/5] Получение SSL сертификата от Let's Encrypt..."
echo "   Это может занять 1-2 минуты..."

# Получаем сертификат (с автоматической настройкой nginx)
certbot --nginx \
    -d kkt-box.net \
    -d www.kkt-box.net \
    --non-interactive \
    --agree-tos \
    --email master@relabs.center \
    --redirect

echo "✅ SSL сертификат получен и установлен"

# Шаг 5: Настройка финальной конфигурации Nginx с оптимизациями
echo ""
echo "⚙️  [5/5] Применение оптимизированной конфигурации..."

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
    
    # Размер загружаемых файлов
    client_max_body_size 100M;
    
    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Стандартные таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Специальный таймаут для восстановления БД
    location /api/database/restore {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Увеличенные таймауты
        proxy_connect_timeout 180s;
        proxy_send_timeout 180s;
        proxy_read_timeout 180s;
        
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Статические файлы
    location / {
        root /home/kktapp/kkt-system/web/app/static;
        try_files $uri $uri/ /dashboard.html;
        index dashboard.html;
    }
    
    # Бэкапы (защищенный доступ)
    location /backups/ {
        internal;
        alias /home/kktapp/kkt-system/backups/;
    }
}

# Fallback для прямого доступа по IP
server {
    listen 443 ssl http2;
    server_name 185.185.71.248;
    
    ssl_certificate /etc/letsencrypt/live/kkt-box.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kkt-box.net/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Редирект на основной домен
    return 301 https://kkt-box.net$request_uri;
}
EOF

# Проверка и применение
nginx -t && systemctl reload nginx

echo ""
echo "✅ HTTPS успешно настроен!"
echo ""
echo "📋 Информация о сертификате:"
certbot certificates

echo ""
echo "🔄 Автоматическое обновление:"
echo "   Certbot автоматически обновит сертификат через systemd timer"
systemctl status certbot.timer --no-pager | head -5

echo ""
echo "🌐 Доступ к системе:"
echo "   https://kkt-box.net"
echo "   https://www.kkt-box.net"
echo ""
echo "✅ Готово! Все HTTP запросы будут автоматически перенаправлены на HTTPS"
