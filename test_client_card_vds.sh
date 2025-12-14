#!/bin/bash

# Тест API карточки клиента на VDS
SERVER="http://kkt-box.net:8080"
EMAIL="admin@kkt.local"
PASSWORD="admin123"

echo "=== ТЕСТ API КАРТОЧКИ КЛИЕНТА НА VDS ==="
echo ""

# 1. Авторизация
echo "1. Получение JWT токена..."
TOKEN_RESPONSE=$(curl -s -X POST "$SERVER/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "Ответ авторизации: $TOKEN_RESPONSE"
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ ОШИБКА: Не удалось получить токен"
    exit 1
fi

echo "✓ Токен получен: ${TOKEN:0:20}..."
echo ""

# 2. Получить список клиентов
echo "2. Получение списка пользователей (клиентов)..."
USERS_RESPONSE=$(curl -s -X GET "$SERVER/api/users?role=client&page_size=10" \
  -H "Authorization: Bearer $TOKEN")

echo "Пользователи (первые 500 символов):"
echo "$USERS_RESPONSE" | head -c 500
echo ""

# Извлекаем ID первого клиента
USER_ID=$(echo $USERS_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$USER_ID" ]; then
    echo "❌ ОШИБКА: Не найдено ни одного клиента"
    exit 1
fi

echo "✓ Найден клиент с ID: $USER_ID"
echo ""

# 3. Получить полные детали клиента
echo "3. Получение полных деталей клиента ID=$USER_ID..."
DETAILS_RESPONSE=$(curl -s -X GET "$SERVER/api/users/$USER_ID/full-details" \
  -H "Authorization: Bearer $TOKEN")

echo "Полный ответ:"
echo "$DETAILS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DETAILS_RESPONSE"
echo ""

# 4. Проверить наличие ключевых полей
echo "4. Проверка структуры данных..."
echo "$DETAILS_RESPONSE" | grep -q '"cash_registers"' && echo "✓ Поле cash_registers найдено" || echo "❌ Поле cash_registers НЕ найдено"
echo "$DETAILS_RESPONSE" | grep -q '"register_deadlines"' && echo "✓ Поле register_deadlines найдено" || echo "❌ Поле register_deadlines НЕ найдено"
echo "$DETAILS_RESPONSE" | grep -q '"general_deadlines"' && echo "✓ Поле general_deadlines найдено" || echo "❌ Поле general_deadlines НЕ найдено"
echo "$DETAILS_RESPONSE" | grep -q '"name"' && echo "✓ Поле name найдено" || echo "❌ Поле name НЕ найдено"
echo ""

# 5. Проверить типы дедлайнов
echo "5. Получение типов дедлайнов..."
TYPES_RESPONSE=$(curl -s -X GET "$SERVER/api/deadline-types" \
  -H "Authorization: Bearer $TOKEN")

echo "Типы дедлайнов:"
echo "$TYPES_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TYPES_RESPONSE"
echo ""

# 6. Проверить провайдеров ОФД
echo "6. Получение провайдеров ОФД..."
OFD_RESPONSE=$(curl -s -X GET "$SERVER/api/ofd-providers" \
  -H "Authorization: Bearer $TOKEN")

echo "Провайдеры ОФД:"
echo "$OFD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$OFD_RESPONSE"
echo ""

echo "=== ТЕСТ ЗАВЕРШЕН ==="
