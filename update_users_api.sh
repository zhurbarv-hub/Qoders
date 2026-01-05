#!/bin/bash
# Скрипт для обновления users.py на VDS

# Добавляем поля register_name и installation_address в API ответ
cd /home/kktapp/kkt-system/web/app/api

# Создаем backup
cp users.py users.py.backup_$(date +%Y%m%d_%H%M%S)

# Добавляем строки после "model": reg.model,
sed -i '/\"model\": reg\.model,/a\                "register_name": reg.register_name,\n                "installation_address": reg.installation_address,' users.py

echo "✅ Файл users.py обновлен"
echo "Проверка изменений:"
grep -A 4 '"model": reg.model' users.py | head -7

# Перезапуск сервиса
echo "Перезапуск kkt-web..."
systemctl restart kkt-web
sleep 3
systemctl status kkt-web --no-pager | head -15
