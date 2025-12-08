# Тестирование Backend API - Фаза 2

## Быстрый старт

### 1. Подготовка окружения

```bash
# Активировать виртуальное окружение
venv\Scripts\activate

# Убедиться, что все зависимости установлены
pip install -r requirements.txt
```

### 2. Проверка конфигурации

```bash
# Проверить настройки
python backend\config.py

# Проверить подключение к БД
python backend\database.py
```

### 3. Запуск сервера

```bash
# Запустить через batch-файл
start_backend.bat

# Или напрямую
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Доступ к документации

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Тестирование через Swagger UI

### Шаг 1: Вход в систему

1. Откройте http://localhost:8000/docs
2. Найдите `POST /api/auth/login`
3. Нажмите "Try it out"
4. Введите данные:
   ```json
   {
     "email": "admin@kkt.local",
     "password": "admin123"
   }
   ```
5. Нажмите "Execute"
6. Скопируйте `access_token` из ответа

### Шаг 2: Авторизация в Swagger

1. Нажмите кнопку "Authorize" вверху страницы
2. Введите: `Bearer {ваш_access_token}`
3. Нажмите "Authorize"
4. Теперь все запросы будут авторизованы

### Шаг 3: Тестирование эндпоинтов

#### Получить статистику дашборда
```
GET /api/dashboard/summary
```

#### Список клиентов
```
GET /api/clients?page=1&limit=10
```

#### Создать клиента
```json
POST /api/clients
{
  "name": "ООО Тестовая Компания",
  "inn": "1234567890",
  "contact_person": "Иван Иванов",
  "phone": "+79161234567",
  "email": "test@example.com"
}
```

#### Создать дедлайн
```json
POST /api/deadlines
{
  "client_id": 1,
  "deadline_type_id": 1,
  "expiration_date": "2025-03-15",
  "notes": "Тестовый дедлайн"
}
```

---

## Тестирование через curl

### Получить токен
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@kkt.local\",\"password\":\"admin123\"}"
```

### Получить список клиентов
```bash
curl -X GET "http://localhost:8000/api/clients" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Создать клиента
```bash
curl -X POST "http://localhost:8000/api/clients" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"ООО Тест\",\"inn\":\"9999999999\"}"
```

---

## Проверка здоровья системы

### Health Check
```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": 1234567890.123
}
```

---

## Чек-лист тестирования Фазы 2

### Аутентификация ✓
- [ ] Вход с корректными данными → 200 OK
- [ ] Вход с неверным паролем → 401 Unauthorized
- [ ] Вход с несуществующим email → 401 Unauthorized
- [ ] Выход из системы → 200 OK
- [ ] Получение информации о пользователе → 200 OK

### Клиенты ✓
- [ ] Список клиентов с пагинацией → 200 OK
- [ ] Поиск клиентов по имени/ИНН → 200 OK
- [ ] Получение клиента по ID → 200 OK
- [ ] Создание клиента с корректными данными → 201 Created
- [ ] Создание с дубликатом ИНН → 409 Conflict
- [ ] Обновление клиента → 200 OK
- [ ] Удаление клиента (soft delete) → 200 OK

### Дедлайны ✓
- [ ] Список дедлайнов с фильтрацией → 200 OK
- [ ] Фильтрация по client_id → 200 OK
- [ ] Фильтрация по статусу (green/yellow/red) → 200 OK
- [ ] Получение дедлайна по ID → 200 OK
- [ ] Создание дедлайна → 201 Created
- [ ] Создание с несуществующим client_id → 404 Not Found
- [ ] Обновление дедлайна → 200 OK
- [ ] Удаление дедлайна → 200 OK

### Дашборд ✓
- [ ] Получение статистики → 200 OK
- [ ] Проверка подсчёта по статусам → Корректные числа
- [ ] Список срочных дедлайнов → Сортировка по дате

### Типы дедлайнов ✓
- [ ] Список типов → 200 OK
- [ ] Создание кастомного типа (admin) → 201 Created
- [ ] Обновление кастомного типа → 200 OK
- [ ] Попытка изменить системный тип → 400 Bad Request
- [ ] Деактивация типа → 200 OK

### Контакты ✓
- [ ] Список контактов клиента → 200 OK
- [ ] Добавление контакта → 201 Created
- [ ] Дубликат telegram_id → 409 Conflict
- [ ] Обновление контакта → 200 OK
- [ ] Удаление контакта → 200 OK
- [ ] Переключение уведомлений → 200 OK

### Валидация ✓
- [ ] ИНН: только цифры, 10 или 12 символов
- [ ] Телефон: российский формат +7XXXXXXXXXX
- [ ] Email: корректный формат
- [ ] Даты: корректный формат

### Безопасность ✓
- [ ] Доступ без токена → 401 Unauthorized
- [ ] Доступ с невалидным токеном → 401 Unauthorized
- [ ] Доступ с истёкшим токеном → 401 Unauthorized
- [ ] Admin эндпоинты требуют роль admin → 403 Forbidden

---

## Известные проблемы и решения

### Проблема: ModuleNotFoundError
**Решение:** Убедитесь, что запускаете из корня проекта и venv активирован

### Проблема: Database connection failed
**Решение:** Проверьте путь в .env и выполните `python database/init_database.py`

### Проблема: JWT secret key error
**Решение:** Сгенерируйте секретный ключ: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

## Следующие шаги

После успешного тестирования Фазы 2:
1. ✅ Все эндпоинты работают
2. ✅ Валидация корректна
3. ✅ Аутентификация функционирует
4. ➡️ Переход к Фазе 3: Telegram Bot Implementation
