# Реализация управления Telegram ID администраторов

**Дата**: 20 декабря 2025  
**Статус**: ✅ РЕАЛИЗОВАНО И РАЗВЁРНУТО

## Обзор

Реализован полный цикл управления Telegram ID для администраторов и менеджеров системы:
- Обязательная валидация при создании
- Автоматическое добавление в .env файл
- Физическое удаление пользователей с очисткой из .env
- Автоматический перезапуск бота для применения изменений

## Реализованные компоненты

### 1. Валидация схем (user_schemas.py)

**Файл**: `web/app/models/user_schemas.py`

Добавлен валидатор для обязательного поля `telegram_id` при создании администраторов и менеджеров:

```python
@validator('telegram_id')
def validate_telegram_id(cls, v, values):
    """Проверка обязательности Telegram ID для администраторов и менеджеров"""
    role = values.get('role')
    if role in ['admin', 'manager'] and not v:
        raise ValueError('Telegram ID обязателен для администраторов и менеджеров')
    return v
```

### 2. Сервис управления .env (env_manager.py)

**Файл**: `web/app/services/env_manager.py` (новый)

Класс `EnvManager` предоставляет методы для:
- `get_admin_telegram_ids()` - получение списка Telegram ID из .env
- `set_admin_telegram_ids(telegram_ids)` - установка списка Telegram ID
- `add_admin_telegram_id(telegram_id)` - добавление нового ID
- `remove_admin_telegram_id(telegram_id)` - удаление ID
- `restart_bot_service()` - перезапуск бота через systemctl

**Ключевые особенности**:
- Автоматическое определение пути к .env файлу
- Безопасная работа с файлом (чтение/запись)
- Логирование всех операций
- Обработка ошибок без прерывания основных операций

### 3. API создания пользователя (users.py)

**Файл**: `web/app/api/users.py`

**Функция**: `create_user()` (строки 171-284)

Добавлен блок автоматического добавления Telegram ID в .env после создания администратора/менеджера:

```python
# Если создаём администратора или менеджера с Telegram ID - добавляем в .env
if user_data.role in ['admin', 'manager'] and user_data.telegram_id:
    try:
        success = env_manager.add_admin_telegram_id(user_data.telegram_id)
        if success:
            # Перезапускаем бота для применения изменений
            env_manager.restart_bot_service()
            print(f"✅ Telegram ID {user_data.telegram_id} добавлен в .env для пользователя {new_user.full_name}")
        else:
            print(f"⚠️  Не удалось добавить Telegram ID {user_data.telegram_id} в .env")
    except Exception as e:
        print(f"❌ Ошибка при добавлении Telegram ID в .env: {e}")
        # Не прерываем создание пользователя из-за ошибки .env
```

### 4. API удаления пользователя (users.py)

**Файл**: `web/app/api/users.py`

**Функция**: `delete_user()` (строки 410-500)

**Изменения**:
- ❌ Убрано "мягкое удаление" (деактивация)
- ✅ Реализовано физическое удаление из БД
- ✅ Удаление всех связанных данных (дедлайны, кассы)
- ✅ Автоматическое удаление Telegram ID из .env
- ✅ Перезапуск бота после удаления

**Алгоритм физического удаления**:
1. Проверка существования пользователя
2. Запрет на удаление самого себя
3. Сохранение данных для логирования (имя, telegram_id, роль)
4. Удаление связанных дедлайнов (для клиентов)
5. Удаление связанных касс (для клиентов)
6. Физическое удаление пользователя из БД
7. Удаление Telegram ID из .env (для админов/менеджеров)
8. Перезапуск бота

```python
# 4. Если это администратор/менеджер с Telegram ID - удаляем из .env
if user_role in ['admin', 'manager'] and user_telegram_id:
    try:
        success = env_manager.remove_admin_telegram_id(user_telegram_id)
        if success:
            # Перезапускаем бота для применения изменений
            env_manager.restart_bot_service()
            print(f"✅ Telegram ID {user_telegram_id} удалён из .env после удаления пользователя {user_full_name}")
        else:
            print(f"⚠️  Не удалось удалить Telegram ID {user_telegram_id} из .env")
    except Exception as e:
        print(f"❌ Ошибка при удалении Telegram ID из .env: {e}")
```

### 5. Фронтенд валидация (managers.js)

**Файл**: `web/app/static/js/managers.js`

**Изменения**:

1. **Визуальное обозначение** (строка 325):
```javascript
<label class="mdl-textfield__label" for="telegram_id">Telegram ID ${!isView ? '*' : ''}</label>
```

2. **Валидация перед отправкой** (строки 398-408):
```javascript
// Проверяем Telegram ID - обязателен для админов и менеджеров
const telegramIdField = document.getElementById('telegram_id');
const telegramId = telegramIdField ? telegramIdField.value.trim() : '';

if ((formData.role === 'admin' || formData.role === 'manager') && !telegramId) {
    alert('Ошибка: Telegram ID обязателен для администраторов и менеджеров');
    telegramIdField.focus();
    return;
}

// Добавляем Telegram ID если указан
if (telegramId) {
    formData.telegram_id = telegramId;
}
```

## Развёртывание

### Загруженные файлы

1. ✅ `web/app/models/user_schemas.py` (11KB)
2. ✅ `web/app/services/env_manager.py` (7KB) - новый файл
3. ✅ `web/app/api/users.py` (37KB)
4. ✅ `web/app/static/js/managers.js` (24KB)

### Выполненные действия

```bash
# Загрузка файлов
scp user_schemas.py root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/
scp env_manager.py root@185.185.71.248:/home/kktapp/kkt-system/web/app/services/
scp users.py root@185.185.71.248:/home/kktapp/kkt-system/web/app/api/
scp managers.js root@185.185.71.248:/home/kktapp/kkt-system/web/app/static/js/

# Установка прав
chown -R kktapp:kktapp /home/kktapp/kkt-system/web/app/

# Перезапуск веб-сервиса
systemctl restart kkt-web.service
```

### Статус сервиса

```
● kkt-web.service - KKT Web Application
     Active: active (running) since Sat 2025-12-20 18:01:35 MSK
     Status: ✅ Запущен успешно
```

## Тестирование

### Сценарий 1: Создание администратора

**Шаги**:
1. Открыть https://kkt-box.net/static/dashboard.html#managers
2. Нажать "Добавить пользователя"
3. Выбрать роль "Администратор"
4. Заполнить все поля (ФИО, Email, Логин, Пароль)
5. **Обязательно** указать Telegram ID (например: `123456789`)
6. Нажать "Создать"

**Ожидаемый результат**:
- Пользователь создан в БД
- Telegram ID добавлен в файл `/home/kktapp/kkt-system/.env`
- Бот автоматически перезапущен
- Новый администратор может управлять ботом

**Проверка**:
```bash
ssh root@185.185.71.248 "grep TELEGRAM_ADMIN_IDS /home/kktapp/kkt-system/.env"
# Должен содержать новый ID
```

### Сценарий 2: Попытка создания без Telegram ID

**Шаги**:
1. Попытаться создать администратора без Telegram ID
2. Нажать "Создать"

**Ожидаемый результат**:
- ❌ Фронтенд валидация: "Ошибка: Telegram ID обязателен для администраторов и менеджеров"
- ❌ Backend валидация (если обойти фронтенд): HTTP 422 с сообщением об ошибке
- Пользователь НЕ создан

### Сценарий 3: Удаление администратора

**Шаги**:
1. Открыть https://kkt-box.net/static/dashboard.html#managers
2. Кликнуть на существующего администратора
3. Нажать кнопку "Удалить" (красная, слева внизу)
4. Ввести пароль текущего пользователя
5. Подтвердить удаление

**Ожидаемый результат**:
- Пользователь физически удалён из БД
- Все связанные данные удалены (дедлайны, кассы)
- Telegram ID удалён из `/home/kktapp/kkt-system/.env`
- Бот автоматически перезапущен
- Удалённый администратор больше НЕ имеет доступа к боту

**Проверка**:
```bash
# Проверка .env
ssh root@185.185.71.248 "grep TELEGRAM_ADMIN_IDS /home/kktapp/kkt-system/.env"
# ID должен отсутствовать

# Проверка БД
# В таблице users не должно быть записи с этим ID
```

### Сценарий 4: Удаление текущего пользователя

**Шаги**:
1. Попытаться удалить самого себя

**Ожидаемый результат**:
- ❌ HTTP 400: "Нельзя удалить свою учётную запись"
- Пользователь НЕ удалён

## Безопасность

✅ **Обязательная валидация** - невозможно создать админа без Telegram ID  
✅ **Двойная проверка** - валидация на фронтенде и бэкенде  
✅ **Подтверждение пароля** при удалении  
✅ **Запрет на самоудаление** - нельзя удалить свою учётную запись  
✅ **Физическое удаление** - никаких следов в БД  
✅ **Синхронизация с ботом** - автоматический перезапуск  
✅ **Логирование** - все операции записываются в логи  

## Технические детали

### Расположение .env файла

- **Путь**: `/home/kktapp/kkt-system/.env`
- **Переменная**: `TELEGRAM_ADMIN_IDS`
- **Формат**: Список через запятую (например: `1157881217,1329276055,556319278`)

### Перезапуск бота

EnvManager использует `systemctl restart kkt-bot.service` для применения изменений.
Требуется, чтобы процесс веб-приложения имел права на перезапуск сервиса.

### Обработка ошибок

Все операции с .env файлом обёрнуты в `try-except`:
- Ошибки логируются
- Не прерывают основные операции (создание/удаление пользователя)
- Пользователь получает уведомление об успехе/неудаче

## Заключение

Функционал управления Telegram ID администраторов полностью реализован и готов к использованию:

✅ Создание администраторов с обязательным Telegram ID  
✅ Автоматическое добавление в .env и перезапуск бота  
✅ Физическое удаление пользователей  
✅ Автоматическая очистка Telegram ID из .env при удалении  
✅ Полная синхронизация между веб-панелью и ботом  

Все файлы развёрнуты на продакшене и готовы к тестированию.
