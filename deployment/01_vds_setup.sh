#!/bin/bash
# ============================================
# Phase 2: VDS Environment Setup
# Скрипт для автоматической настройки VDS сервера
# ============================================

set -e  # Остановка при ошибке

echo "=================================================="
echo "Phase 2: VDS Environment Setup"
echo "=================================================="

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root (sudo)" 
   exit 1
fi

echo "✓ Права root подтверждены"

# ============================================
# 1. Обновление системы
# ============================================
echo ""
echo ">>> Шаг 1/7: Обновление системы..."
apt update
apt upgrade -y
echo "✓ Система обновлена"

# ============================================
# 2. Установка системных утилит
# ============================================
echo ""
echo ">>> Шаг 2/7: Установка системных утилит..."
apt install -y build-essential git curl wget unzip htop net-tools vim
echo "✓ Системные утилиты установлены"

# ============================================
# 3. Установка Python
# ============================================
echo ""
echo ">>> Шаг 3/7: Установка Python 3.11..."
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
echo "✓ Python 3.11 установлен"

# Проверка версии
python3.11 --version

# ============================================
# 4. Установка PostgreSQL
# ============================================
echo ""
echo ">>> Шаг 4/7: Установка PostgreSQL..."
apt install -y postgresql postgresql-contrib libpq-dev
systemctl start postgresql
systemctl enable postgresql
echo "✓ PostgreSQL установлен и запущен"

# Проверка статуса
systemctl status postgresql --no-pager

# ============================================
# 5. Установка Nginx
# ============================================
echo ""
echo ">>> Шаг 5/7: Установка Nginx..."
apt install -y nginx
systemctl start nginx
systemctl enable nginx
echo "✓ Nginx установлен и запущен"

# ============================================
# 6. Установка Certbot для SSL
# ============================================
echo ""
echo ">>> Шаг 6/7: Установка Certbot..."
apt install -y certbot python3-certbot-nginx
echo "✓ Certbot установлен"

# ============================================
# 7. Настройка Firewall (UFW)
# ============================================
echo ""
echo ">>> Шаг 7/7: Настройка Firewall..."
apt install -y ufw

# Настройка правил
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 8080/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Включение firewall
echo "y" | ufw enable

echo "✓ Firewall настроен"

# Показать статус
ufw status verbose

# ============================================
# Итоговая информация
# ============================================
echo ""
echo "=================================================="
echo "✅ Phase 2: VDS Environment Setup - COMPLETE"
echo "=================================================="
echo ""
echo "Установлено:"
echo "  - Python: $(python3.11 --version)"
echo "  - PostgreSQL: $(psql --version)"
echo "  - Nginx: $(nginx -v 2>&1)"
echo "  - Certbot: $(certbot --version)"
echo ""
echo "Следующий шаг:"
echo "  1. Создайте пользователя приложения: adduser kktapp"
echo "  2. Настройте PostgreSQL (скрипт 02_database_setup.sh)"
echo "=================================================="
