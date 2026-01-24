#!/bin/bash
# ============================================
# Полный скрипт развертывания KKT системы
# Запускать с правами root на Ubuntu 24.04
# ============================================

set -e  # Остановка при ошибках

DEPLOYMENT_DIR="/root/kkt-deployment"
APP_USER="kktapp"
DB_NAME="kkt_production"
DB_USER="kkt_user"
DB_PASSWORD="ChangeThisStrongPassword123!"

echo "=========================================="
echo "  KKT System Production Deployment"
echo "=========================================="
echo ""

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Этот скрипт должен быть запущен с правами root"
   exit 1
fi

echo "Current directory: $(pwd)"
echo "Deployment files directory: $DEPLOYMENT_DIR"
echo ""

# ============================================
# Phase 1: Обновление системы
# ============================================
echo ">>> Phase 1/8: Обновление системы Ubuntu..."
apt update -y
apt upgrade -y
echo "✅ Система обновлена"
echo ""

# ============================================
# Phase 2: Установка базовых пакетов
# ============================================
echo ">>> Phase 2/8: Установка базовых пакетов..."
apt install -y build-essential git curl wget unzip htop net-tools vim
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
apt install -y postgresql postgresql-contrib libpq-dev
apt install -y nginx
apt install -y ufw

echo "✅ Базовые пакеты установлены"
echo ""

# ============================================
# Phase 3: Настройка Firewall
# ============================================
echo ">>> Phase 3/8: Настройка Firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 8080/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
echo "y" | ufw enable

echo "✅ Firewall настроен"
ufw status verbose
echo ""

# ============================================
# Phase 4: Настройка PostgreSQL
# ============================================
echo ">>> Phase 4/8: Настройка PostgreSQL..."

systemctl start postgresql
systemctl enable postgresql

# Создание пользователя и базы данных
sudo -u postgres psql <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

SELECT 'User check' as status, EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') as user_exists;

DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME') THEN
        CREATE DATABASE $DB_NAME OWNER $DB_USER ENCODING 'UTF8';
    END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "✅ PostgreSQL настроен"
echo ""

# ============================================
# Phase 5: Создание пользователя приложения
# ============================================
echo ">>> Phase 5/8: Создание пользователя приложения..."

if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    echo "✅ Пользователь $APP_USER создан"
else
    echo "ℹ️  Пользователь $APP_USER уже существует"
fi
echo ""

# ============================================
# Phase 6: Клонирование репозитория
# ============================================
echo ">>> Phase 6/8: Клонирование репозитория..."

APP_DIR="/home/$APP_USER/kkt-system"

# Удаляем старую директорию если существует
if [ -d "$APP_DIR" ]; then
    echo "⚠️  Удаление старой директории $APP_DIR"
    rm -rf "$APP_DIR"
fi

# Клонирование
cd /home/$APP_USER
sudo -u $APP_USER git clone https://github.com/zhurbarv-hub/Qoders.git kkt-system

cd $APP_DIR

echo "✅ Репозиторий склонирован"
echo ""

# ============================================
# Phase 7: Настройка приложения
# ============================================
echo ">>> Phase 7/8: Настройка приложения..."

# Создание venv
sudo -u $APP_USER python3.11 -m venv venv

# Установка зависимостей
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install -r requirements-web.txt"
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install psycopg2-binary"

# Копирование .env файла
if [ -f "$DEPLOYMENT_DIR/.env.production" ]; then
    cp "$DEPLOYMENT_DIR/.env.production" "$APP_DIR/.env"
    chown $APP_USER:$APP_USER "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
    echo "✅ .env файл скопирован"
else
    echo "⚠️  .env.production не найден, создаем из шаблона"
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    chown $APP_USER:$APP_USER "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
fi

# Применение схемы БД
echo "Применение схемы базы данных..."
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -h localhost -f "$APP_DIR/database/schema_postgres.sql"

# Вставка провайдеров ОФД
if [ -f "$APP_DIR/database/insert_ofd_providers.sql" ]; then
    PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -h localhost -f "$APP_DIR/database/insert_ofd_providers.sql" || true
fi

echo "✅ Приложение настроено"
echo ""

# ============================================
# Phase 8: Настройка systemd сервисов
# ============================================
echo ">>> Phase 8/8: Настройка systemd сервисов..."

# Создание директории для логов
mkdir -p /var/log/kkt-system
chown $APP_USER:$APP_USER /var/log/kkt-system

# Создание сервиса для веб-приложения
cat > /etc/systemd/system/kkt-web.service <<EOF
[Unit]
Description=KKT Web Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/uvicorn web.app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Создание сервиса для Telegram бота
cat > /etc/systemd/system/kkt-bot.service <<EOF
[Unit]
Description=KKT Telegram Bot
After=network.target kkt-web.service
Requires=kkt-web.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd и запуск сервисов
systemctl daemon-reload
systemctl enable kkt-web.service
systemctl enable kkt-bot.service
systemctl start kkt-web.service
systemctl start kkt-bot.service

echo "✅ Systemd сервисы настроены и запущены"
echo ""

# ============================================
# Настройка Nginx
# ============================================
echo ">>> Настройка Nginx..."

cat > /etc/nginx/sites-available/kkt-system <<'NGINX_EOF'
upstream kkt_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 8080;
    server_name _;
    
    # Статические файлы
    location /static/ {
        alias /home/kktapp/kkt-system/web/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API и динамический контент
    location / {
        proxy_pass http://kkt_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Увеличенные таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
}
NGINX_EOF

# Активация конфигурации
ln -sf /etc/nginx/sites-available/kkt-system /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверка и перезагрузка Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx

echo "✅ Nginx настроен"
echo ""

# ============================================
# Настройка автоматических бэкапов
# ============================================
echo ">>> Настройка автоматических бэкапов..."

BACKUP_DIR="/home/$APP_USER/backups"
mkdir -p $BACKUP_DIR
chown $APP_USER:$APP_USER $BACKUP_DIR

cat > /home/$APP_USER/backup-database.sh <<'BACKUP_EOF'
#!/bin/bash
BACKUP_DIR="/home/kktapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="kkt_production"
DB_USER="kkt_user"

mkdir -p $BACKUP_DIR

# Создание бэкапа
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/kkt_backup_$DATE.sql.gz

# Удаление старых бэкапов (храним 7 дней)
find $BACKUP_DIR -name "kkt_backup_*.sql.gz" -mtime +7 -delete

echo "$(date): Backup completed - kkt_backup_$DATE.sql.gz" >> /var/log/kkt-system/backup.log
BACKUP_EOF

chmod +x /home/$APP_USER/backup-database.sh
chown $APP_USER:$APP_USER /home/$APP_USER/backup-database.sh

# Добавление в crontab для пользователя kktapp
sudo -u $APP_USER bash -c "(crontab -l 2>/dev/null | grep -v 'backup-database.sh'; echo '0 3 * * * /home/kktapp/backup-database.sh') | crontab -"

echo "✅ Автоматические бэкапы настроены (ежедневно в 3:00)"
echo ""

# ============================================
# Итоговая информация
# ============================================
echo "=========================================="
echo "  ✅ Развертывание завершено успешно!"
echo "=========================================="
echo ""
echo "📊 Статус сервисов:"
systemctl status kkt-web.service --no-pager -l | head -n 5
systemctl status kkt-bot.service --no-pager -l | head -n 5
echo ""
echo "🌐 Доступ к веб-интерфейсу:"
echo "   http://185.185.71.18:8080"
echo ""
echo "🔐 Учетные данные по умолчанию:"
echo "   Email: admin@kkt-system.ru"
echo "   Пароль: admin"
echo ""
echo "📝 Полезные команды:"
echo "   Логи веб-приложения: sudo journalctl -u kkt-web.service -f"
echo "   Логи бота: sudo journalctl -u kkt-bot.service -f"
echo "   Перезапуск: sudo systemctl restart kkt-web kkt-bot"
echo ""
echo "🔒 Не забудьте:"
echo "   1. Изменить пароль администратора"
echo "   2. Обновить Telegram ID администратора в БД"
echo "   3. Настроить SSL (если нужен домен)"
echo ""
echo "=========================================="
