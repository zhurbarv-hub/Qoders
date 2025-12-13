#!/bin/bash
# ============================================
# Phase 5: Nginx and SSL Setup
# Скрипт для настройки Nginx reverse proxy и SSL
# ============================================

set -e

echo "=================================================="
echo "Phase 5: Nginx and SSL Setup"
echo "=================================================="

# Параметры
DOMAIN="${DOMAIN:-example.com}"
APP_USER="kktapp"
STATIC_DIR="/home/$APP_USER/kkt-system/web/app/static"

echo ""
echo "Настройка для домена: $DOMAIN"
echo ""

if [ "$DOMAIN" = "example.com" ]; then
    echo "⚠️ ВНИМАНИЕ: Установите переменную DOMAIN перед запуском:"
    echo "   export DOMAIN=your-domain.com"
    echo "   ./05_nginx_setup.sh"
    echo ""
    read -p "Введите ваш домен: " DOMAIN
fi

# ============================================
# 1. Создание конфигурации Nginx
# ============================================
echo ""
echo ">>> Шаг 1/4: Создание конфигурации Nginx..."

cat > /etc/nginx/sites-available/kkt-system <<EOF
upstream kkt_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# HTTP сервер (редирект на HTTPS будет добавлен certbot)
server {
    listen 80;
    server_name $DOMAIN;

    # Статические файлы
    location /static/ {
        alias $STATIC_DIR/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API и динамический контент
    location / {
        proxy_pass http://kkt_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://kkt_backend;
        access_log off;
    }
}
EOF

echo "✓ Конфигурация Nginx создана"

# ============================================
# 2. Активация конфигурации
# ============================================
echo ""
echo ">>> Шаг 2/4: Активация конфигурации..."

# Создание симлинка
ln -sf /etc/nginx/sites-available/kkt-system /etc/nginx/sites-enabled/

# Удаление дефолтной конфигурации
rm -f /etc/nginx/sites-enabled/default

# Проверка синтаксиса
nginx -t

echo "✓ Конфигурация активирована"

# ============================================
# 3. Перезапуск Nginx
# ============================================
echo ""
echo ">>> Шаг 3/4: Перезапуск Nginx..."

systemctl restart nginx

echo "✓ Nginx перезапущен"

# ============================================
# 4. Настройка SSL с Let's Encrypt
# ============================================
echo ""
echo ">>> Шаг 4/4: Настройка SSL сертификата..."

echo ""
echo "Установка SSL сертификата для домена: $DOMAIN"
echo ""

# Запуск certbot
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

echo "✓ SSL сертификат установлен"

# Проверка авто-обновления
systemctl status certbot.timer --no-pager

# ============================================
# Итоговая информация
# ============================================
echo ""
echo "=================================================="
echo "✅ Phase 5: Nginx and SSL - COMPLETE"
echo "=================================================="
echo ""
echo "Конфигурация:"
echo "  Домен: $DOMAIN"
echo "  HTTP: http://$DOMAIN (→ HTTPS redirect)"
echo "  HTTPS: https://$DOMAIN"
echo "  Статика: https://$DOMAIN/static/"
echo ""
echo "SSL сертификат:"
echo "  Провайдер: Let's Encrypt"
echo "  Авто-обновление: Да (certbot.timer)"
echo ""
echo "Проверка:"
echo "  curl http://$DOMAIN/health"
echo "  curl https://$DOMAIN/health"
echo ""
echo "Следующий шаг:"
echo "  - Протестируйте систему в браузере"
echo "  - Настройте бэкапы (скрипт 06_backup_setup.sh)"
echo "=================================================="
