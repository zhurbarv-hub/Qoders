#!/bin/bash

echo "Изменение схемы БД: делаем deadline_type_id nullable..."
sudo -u postgres psql -d kkt_production -c "ALTER TABLE deadlines ALTER COLUMN deadline_type_id DROP NOT NULL;"

echo "Проверка изменения..."
sudo -u postgres psql -d kkt_production -c "SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name = 'deadlines' AND column_name = 'deadline_type_id';"

echo "Установка прав на файл API..."
chown kktapp:kktapp /home/kktapp/kkt-system/web/app/api/deadline_types.py

echo "Перезапуск веб-сервиса..."
systemctl restart kkt-web.service

echo "Проверка статуса..."
systemctl status kkt-web.service --no-pager | head -10

echo "Готово!"
