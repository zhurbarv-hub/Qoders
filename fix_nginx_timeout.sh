#!/bin/bash
# Скрипт для увеличения nginx timeout для восстановления БД

echo "=== Проверка текущей конфигурации nginx ==="
cat /etc/nginx/sites-available/kkt-system | grep -A 30 "location /api/"

echo ""
echo "=== Создание резервной копии ==="
sudo cp /etc/nginx/sites-available/kkt-system /etc/nginx/sites-available/kkt-system.backup.$(date +%Y%m%d_%H%M%S)

echo ""
echo "=== Обновление конфигурации ==="
# Создаем временный файл с обновленной конфигурацией
sudo tee /tmp/kkt-system.new > /dev/null << 'EOF'
server {
    listen 80;
    server_name 185.185.71.248;

    client_max_body_size 100M;

    # Общие таймауты для всех API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Стандартные таймауты для обычных операций
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # СПЕЦИАЛЬНЫЙ таймаут для восстановления БД
    location /api/database/restore {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Увеличенные таймауты для восстановления
        proxy_connect_timeout 180s;
        proxy_send_timeout 180s;
        proxy_read_timeout 180s;
        
        # Буферизация для больших ответов
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
EOF

echo ""
echo "=== Применение новой конфигурации ==="
sudo mv /tmp/kkt-system.new /etc/nginx/sites-available/kkt-system

echo ""
echo "=== Проверка синтаксиса nginx ==="
sudo nginx -t

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Перезагрузка nginx ==="
    sudo systemctl reload nginx
    echo "✅ Nginx успешно обновлен и перезагружен"
else
    echo "❌ Ошибка в конфигурации, откатываем изменения"
    sudo cp /etc/nginx/sites-available/kkt-system.backup.* /etc/nginx/sites-available/kkt-system
fi

echo ""
echo "=== Проверка статуса nginx ==="
sudo systemctl status nginx --no-pager -l
