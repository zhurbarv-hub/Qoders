#!/bin/bash
# ============================================
# Phase 5: Infrastructure Services Setup
# Скрипт для настройки systemd сервисов
# ============================================

set -e

echo "=================================================="
echo "Phase 5: Systemd Services Setup"
echo "=================================================="

APP_USER="kktapp"
APP_DIR="/home/$APP_USER/kkt-system"

# ============================================
# 1. Создание systemd сервиса для веб-приложения
# ============================================
echo ""
echo ">>> Шаг 1/3: Создание kkt-web.service..."

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
ExecStart=$APP_DIR/venv/bin/uvicorn web.app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ kkt-web.service создан"

# ============================================
# 2. Создание systemd сервиса для Telegram бота
# ============================================
echo ""
echo ">>> Шаг 2/3: Создание kkt-bot.service..."

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

echo "✓ kkt-bot.service создан"

# ============================================
# 3. Активация и запуск сервисов
# ============================================
echo ""
echo ">>> Шаг 3/3: Активация сервисов..."

# Перезагрузка systemd
systemctl daemon-reload

# Включение автозапуска
systemctl enable kkt-web.service
systemctl enable kkt-bot.service

echo "✓ Сервисы активированы для автозапуска"

# Запуск сервисов
echo ""
echo "Запуск сервисов..."
systemctl start kkt-web.service
sleep 3
systemctl start kkt-bot.service

echo "✓ Сервисы запущены"

# Проверка статуса
echo ""
echo "Статус сервисов:"
echo "----------------"
systemctl status kkt-web.service --no-pager
echo ""
systemctl status kkt-bot.service --no-pager

# ============================================
# Итоговая информация
# ============================================
echo ""
echo "=================================================="
echo "✅ Phase 5: Services Setup - COMPLETE"
echo "=================================================="
echo ""
echo "Созданные сервисы:"
echo "  - kkt-web.service (Web Application)"
echo "  - kkt-bot.service (Telegram Bot)"
echo ""
echo "Управление сервисами:"
echo "  Перезапуск: sudo systemctl restart kkt-web.service"
echo "  Статус: sudo systemctl status kkt-web.service"
echo "  Логи: sudo journalctl -u kkt-web.service -f"
echo ""
echo "Следующий шаг:"
echo "  - Настройте Nginx (скрипт 05_nginx_setup.sh)"
echo "=================================================="
