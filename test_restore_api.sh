#!/bin/bash
# Тест восстановления БД с детальным выводом

echo "=== Тестирование API восстановления БД ==="

# Получаем токен (используем существующую сессию или логин)
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"master@relabs.center","password":"your_admin_password"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Не удалось получить токен"
    exit 1
fi

echo "✅ Токен получен: ${TOKEN:0:20}..."

# Тестовый запрос на восстановление
echo ""
echo "=== Отправка запроса на восстановление ==="

curl -v -X POST http://localhost:8000/api/database/restore \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"filename":"backup_20251220_030001.sql","password":"your_admin_password"}' \
  2>&1 | tee /tmp/restore_response.log

echo ""
echo "=== Проверка логов сервиса ==="
journalctl -u kkt-web.service --since "30 seconds ago" --no-pager | tail -50
