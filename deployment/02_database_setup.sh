#!/bin/bash
# ============================================
# Phase 3: Database Setup
# Скрипт для настройки PostgreSQL и создания базы данных
# ============================================

set -e

echo "=================================================="
echo "Phase 3: PostgreSQL Database Setup"
echo "=================================================="

# Параметры базы данных
DB_NAME="kkt_production"
DB_USER="kkt_user"
DB_PASSWORD="${DB_PASSWORD:-ChangeThisStrongPassword123!}"

echo ""
echo "Настройка базы данных:"
echo "  Имя БД: $DB_NAME"
echo "  Пользователь: $DB_USER"
echo ""

# ============================================
# 1. Создание базы данных и пользователя
# ============================================
echo ">>> Шаг 1/4: Создание базы данных и пользователя..."

sudo -u postgres psql <<EOF
-- Создание пользователя
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Создание базы данных
CREATE DATABASE $DB_NAME OWNER $DB_USER ENCODING 'UTF8';

-- Предоставление прав
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Вывод информации
\l $DB_NAME
\du $DB_USER
EOF

echo "✓ База данных и пользователь созданы"

# ============================================
# 2. Настройка PostgreSQL
# ============================================
echo ""
echo ">>> Шаг 2/4: Настройка PostgreSQL для оптимальной производительности..."

# Бэкап оригинальной конфигурации
cp /etc/postgresql/*/main/postgresql.conf /etc/postgresql/*/main/postgresql.conf.backup

# Применение оптимизаций (для 2GB RAM)
sudo -u postgres psql <<EOF
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '1536MB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET max_connections = '100';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
EOF

echo "✓ Конфигурация PostgreSQL обновлена"

# Перезапуск PostgreSQL
systemctl restart postgresql

echo "✓ PostgreSQL перезапущен"

# ============================================
# 3. Проверка подключения
# ============================================
echo ""
echo ">>> Шаг 3/4: Проверка подключения..."

PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -c "SELECT version();"

echo "✓ Подключение к базе данных успешно"

# ============================================
# 4. Применение схемы (если файл доступен)
# ============================================
echo ""
echo ">>> Шаг 4/4: Применение схемы базы данных..."

SCHEMA_FILE="/home/kktapp/kkt-system/database/schema_postgres.sql"

if [ -f "$SCHEMA_FILE" ]; then
    echo "Найден файл схемы: $SCHEMA_FILE"
    PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -f $SCHEMA_FILE
    echo "✓ Схема базы данных применена"
else
    echo "⚠ Файл схемы не найден: $SCHEMA_FILE"
    echo "  Примените схему вручную после клонирования репозитория"
fi

# ============================================
# Итоговая информация
# ============================================
echo ""
echo "=================================================="
echo "✅ Phase 3: Database Setup - COMPLETE"
echo "=================================================="
echo ""
echo "Параметры подключения:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo ""
echo "Connection string для .env файла:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "Следующий шаг:"
echo "  - Склонируйте репозиторий: git clone https://github.com/zhurbarv-hub/Qoders.git"
echo "  - Настройте приложение (скрипт 03_app_setup.sh)"
echo "=================================================="
