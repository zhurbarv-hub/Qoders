#!/bin/bash
# ============================================
# Phase 4: Application Deployment
# Скрипт для развертывания веб-приложения и бота
# ============================================

set -e

echo "=================================================="
echo "Phase 4: Application Deployment"
echo "=================================================="

# Параметры
APP_USER="kktapp"
APP_DIR="/home/$APP_USER/kkt-system"
REPO_URL="https://github.com/zhurbarv-hub/Qoders.git"

# Проверка пользователя
if ! id "$APP_USER" &>/dev/null; then
    echo "Пользователь $APP_USER не существует. Создайте его сначала:"
    echo "  sudo adduser $APP_USER"
    exit 1
fi

echo "✓ Пользователь $APP_USER существует"

# ============================================
# 1. Клонирование репозитория
# ============================================
echo ""
echo ">>> Шаг 1/6: Клонирование репозитория..."

if [ -d "$APP_DIR" ]; then
    echo "Директория $APP_DIR уже существует"
    cd $APP_DIR
    sudo -u $APP_USER git pull
else
    sudo -u $APP_USER git clone $REPO_URL $APP_DIR
fi

cd $APP_DIR
echo "✓ Репозиторий склонирован/обновлён"

# ============================================
# 2. Создание виртуального окружения
# ============================================
echo ""
echo ">>> Шаг 2/6: Создание виртуального окружения..."

sudo -u $APP_USER python3.11 -m venv venv

echo "✓ Виртуальное окружение создано"

# ============================================
# 3. Установка зависимостей
# ============================================
echo ""
echo ">>> Шаг 3/6: Установка Python зависимостей..."

sudo -u $APP_USER bash <<EOF
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-web.txt
pip install psycopg2-binary gunicorn
EOF

echo "✓ Зависимости установлены"

# ============================================
# 4. Создание .env файла
# ============================================
echo ""
echo ">>> Шаг 4/6: Настройка .env файла..."

if [ ! -f "$APP_DIR/.env" ]; then
    echo "Создание .env файла из шаблона..."
    sudo -u $APP_USER cp $APP_DIR/.env.example $APP_DIR/.env
    
    echo ""
    echo "⚠️ ВАЖНО: Отредактируйте файл .env с правильными значениями:"
    echo "  nano $APP_DIR/.env"
    echo ""
    echo "Обязательные переменные:"
    echo "  - DATABASE_URL (PostgreSQL connection string)"
    echo "  - JWT_SECRET_KEY (сгенерируйте сильный ключ)"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - TELEGRAM_ADMIN_IDS"
else
    echo "✓ Файл .env уже существует"
fi

# Установка прав доступа
chmod 600 $APP_DIR/.env
chown $APP_USER:$APP_USER $APP_DIR/.env

echo "✓ .env файл настроен (права 600)"

# ============================================
# 5. Создание директорий для логов
# ============================================
echo ""
echo ">>> Шаг 5/6: Создание директорий..."

mkdir -p /var/log/kkt-system
chown $APP_USER:$APP_USER /var/log/kkt-system

mkdir -p $APP_DIR/backups
chown $APP_USER:$APP_USER $APP_DIR/backups

echo "✓ Директории созданы"

# ============================================
# 6. Тестовый запуск
# ============================================
echo ""
echo ">>> Шаг 6/6: Проверка конфигурации..."

# Проверка импорта модулей
sudo -u $APP_USER bash <<EOF
source venv/bin/activate
python -c "from web.app import main; print('✓ Web app imports OK')"
python -c "from bot import main; print('✓ Bot imports OK')"
EOF

echo "✓ Конфигурация приложения корректна"

# ============================================
# Итоговая информация
# ============================================
echo ""
echo "=================================================="
echo "✅ Phase 4: Application Deployment - COMPLETE"
echo "=================================================="
echo ""
echo "Приложение установлено в: $APP_DIR"
echo ""
echo "Следующие шаги:"
echo "  1. Отредактируйте .env файл:"
echo "     nano $APP_DIR/.env"
echo ""
echo "  2. Примените схему БД (если не сделано):"
echo "     cd $APP_DIR"
echo "     PGPASSWORD=password psql -U kkt_user -d kkt_production -f database/schema_postgres.sql"
echo ""
echo "  3. Настройте systemd сервисы (скрипт 04_services_setup.sh)"
echo "=================================================="
