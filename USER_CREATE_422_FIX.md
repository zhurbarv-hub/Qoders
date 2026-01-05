# Исправление ошибки 422 при создании клиента

**Дата**: 21 декабря 2025  
**Проблема**: Ошибка 422 (Unprocessable Entity) при попытке создать нового клиента через веб-интерфейс

## Описание проблемы

### Симптомы

При попытке создать нового клиента через кнопку "Добавить клиента" в разделе "Управление клиентами" возникала ошибка 422 с сообщением "Unprocessable Entity".

### Логи ошибки

```
Dec 21 12:15:44 box-879432 uvicorn[52513]: INFO: 80.234.38.31:0 - "POST /api/users HTTP/1.0" 422 Unprocessable Entity
```

```javascript
// Консоль браузера
/api/users:1 Failed to load resource: the server responded with a status of 422 ()
users.js:363 Ошибка: Error: [object Object]
    at submitUserForm (users.js:356:19)
```

## Причина ошибки

### Анализ кода

**Файл**: `web/app/static/js/users.js`  
**Функция**: `submitUserForm()` (строки 325-366)

При создании нового клиента отправлялся следующий объект:

```javascript
const formData = {
    company_name: document.getElementById('company_name').value,
    inn: document.getElementById('inn').value,
    full_name: document.getElementById('full_name').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    address: document.getElementById('address').value,
    notes: document.getElementById('notes').value,
    role: 'client',
    is_active: true
    // ❌ ОТСУТСТВУЕТ: username
};
```

### Требования API

**Схема**: `UserCreateByAdmin` в `web/app/models/user_schemas.py`

```python
class UserCreateByAdmin(UserBase):
    """Схема для создания пользователя администратором"""
    username: str = Field(..., min_length=3, max_length=50, 
                         pattern="^[a-zA-Z0-9_]+$", 
                         description="Логин (латинские символы, цифры, подчеркивание)")
    # ... другие поля
```

Поле `username` является **обязательным** при создании пользователя, но не передавалось во фронтенде.

## Решение

### Добавление автогенерации username

Добавлен код автоматической генерации `username` из ИНН клиента перед отправкой данных на сервер.

**Файл**: `web/app/static/js/users.js`  
**Функция**: `submitUserForm()`  
**Изменение**:

```javascript
async function submitUserForm(event, mode, userId) {
    event.preventDefault();
    
    const formData = {
        company_name: document.getElementById('company_name').value,
        inn: document.getElementById('inn').value,
        full_name: document.getElementById('full_name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        address: document.getElementById('address').value,
        notes: document.getElementById('notes').value,
        role: 'client',
        is_active: true
    };
    
    // ✅ ДОБАВЛЕНО: Для создания нового клиента добавляем username (генерируем из ИНН)
    if (mode === 'add') {
        const inn = document.getElementById('inn').value;
        // Генерируем username из ИНН: client_ + ИНН
        formData.username = 'client_' + inn;
    }
    
    // ... остальной код
}
```

### Логика генерации username

**Формат**: `client_{ИНН}`

**Примеры**:
- ИНН: `7707083893` → username: `client_7707083893`
- ИНН: `500100732259` → username: `client_500100732259`

**Обоснование выбора формата**:
1. **Префикс `client_`** - чётко идентифицирует тип пользователя
2. **ИНН в качестве основы** - уникальный идентификатор компании
3. **Простота** - не требует дополнительной валидации или проверок
4. **Соответствие паттерну** - `^[a-zA-Z0-9_]+$` (латинские буквы, цифры, подчёркивание)

### Почему только при создании?

При редактировании (mode === 'edit') поле `username` не добавляется, так как:
- Username нельзя менять после создания (используется для входа)
- Схема `UserUpdate` не включает обязательное поле `username`
- API не требует и не принимает изменения username

## Развёртывание

### Изменённые файлы

1. **users.js** - добавлена генерация username
   ```
   Путь: /home/kktapp/kkt-system/web/app/static/js/users.js
   Размер: 24KB
   ```

2. **dashboard.html** - обновлена версия users.js для сброса кэша
   ```
   Изменение: v=4.13&t=20251220_1910 → v=4.14&t=20251221_1220
   Путь: /home/kktapp/kkt-system/web/app/static/dashboard.html
   ```

### Команды развёртывания

```bash
# 1. Загрузка исправленного users.js
scp d:\QoProj\KKT\web\app\static\js\users.js \
    root@185.185.71.248:/home/kktapp/kkt-system/web/app/static/js/

# 2. Загрузка обновлённого dashboard.html
scp d:\QoProj\KKT\web\app\static\dashboard.html \
    root@185.185.71.248:/home/kktapp/kkt-system/web/app/static/

# 3. Установка прав
ssh root@185.185.71.248 \
    "chown kktapp:kktapp /home/kktapp/kkt-system/web/app/static/js/users.js && \
     chown kktapp:kkt-system/web/app/static/dashboard.html"
```

## Проверка исправления

### Шаги тестирования

1. Открыть дашборд → раздел "Клиенты"
2. Нажать кнопку "Добавить клиента"
3. Заполнить форму:
   - Название компании: **ООО "Тестовая компания"**
   - ИНН: **1234567890**
   - Контактное лицо: **Иван Иванов**
   - Email: **test@example.com**
   - Телефон: **+7 (999) 123-45-67**
4. Нажать "Создать"

### Ожидаемый результат

✅ **Успешное создание клиента**:
- Показывается сообщение: "Клиент успешно создан"
- Клиент появляется в списке
- Username в БД: `client_1234567890`

❌ **Ранее (до исправления)**:
- Ошибка 422: "Unprocessable Entity"
- Клиент не создаётся

### Проверка в базе данных

```sql
SELECT id, username, email, inn, company_name, role 
FROM users 
WHERE inn = '1234567890';

-- Ожидаемый результат:
-- id | username          | email             | inn        | company_name           | role
-- 42 | client_1234567890 | test@example.com  | 1234567890 | ООО "Тестовая компания"| client
```

## Технические детали

### Валидация username на backend

**Схема**: `UserCreateByAdmin`

```python
username: str = Field(
    ..., 
    min_length=3,           # Минимум 3 символа
    max_length=50,          # Максимум 50 символов
    pattern="^[a-zA-Z0-9_]+$",  # Только латинские буквы, цифры, подчёркивание
    description="Логин (латинские символы, цифры, подчеркивание)"
)
```

**Проверка уникальности** в `create_user()`:

```python
existing_username = db.query(User).filter(User.username == user_data.username).first()
if existing_username:
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"Пользователь с логином '{user_data.username}' уже существует"
    )
```

### Потенциальные коллизии

**Проблема**: Два клиента с одинаковым ИНН приведут к конфликту username.

**Решение**: ИНН уже проверяется на уникальность:

```python
if user_data.inn:
    existing_inn = db.query(User).filter(User.inn == user_data.inn).first()
    if existing_inn:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Клиент с ИНН '{user_data.inn}' уже существует"
        )
```

Таким образом, коллизия username невозможна, так как клиент с таким ИНН уже существует.

### Альтернативные подходы

**Вариант 1: Генерация на backend** (не выбран)
```python
# В create_user() API
if not user_data.username and user_data.role == 'client':
    user_data.username = f"client_{user_data.inn}"
```
- ❌ Требует изменения схемы (username становится Optional)
- ❌ Усложняет логику backend
- ✅ Централизованная логика

**Вариант 2: Использование email** (не выбран)
```javascript
formData.username = email.split('@')[0].toLowerCase();
```
- ❌ Может содержать недопустимые символы (точки, дефисы)
- ❌ Не уникален (несколько доменов, одинаковые префиксы)

**Вариант 3: ИНН без префикса** (не выбран)
```javascript
formData.username = inn;
```
- ❌ Непонятно, что это за пользователь (клиент? админ?)
- ✅ Короче и проще

**Выбранный вариант: client_{ИНН}** ✅
- ✅ Уникальность гарантирована ИНН
- ✅ Чёткая идентификация типа пользователя
- ✅ Соответствие паттерну валидации
- ✅ Не требует изменений backend
- ✅ Простота реализации

## Связанные изменения

### История проблемы

Ошибка появилась из-за того, что:
1. Форма создания клиента была реализована без учёта обязательного поля `username`
2. API требует username согласно схеме `UserCreateByAdmin`
3. Фронтенд не генерировал и не отправлял это поле

### Ранее реализованные исправления

В этой же сессии были исправлены:
- ✅ Отображение последнего входа администраторов (поле `last_login`)
- ✅ Синхронизация переключателя автобэкапа
- ✅ Форматирование таблиц и форм

## Заключение

Ошибка 422 при создании клиента полностью исправлена путём добавления автоматической генерации username из ИНН.

**Изменения**:
- ✅ Frontend: добавлена генерация username = `client_{ИНН}`
- ✅ Обновлена версия файла для сброса кэша
- ✅ Развёрнуто на production

**Статус**: ✅ Исправлено и развёрнуто  
**Дата**: 21.12.2025 12:20 MSK  
**Версия файла**: users.js v4.14 (20251221_1220)
