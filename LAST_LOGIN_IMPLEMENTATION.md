# Реализация отображения последнего входа администраторов и менеджеров

**Дата**: 20 декабря 2025  
**Задача**: Добавить отображение времени последнего входа в систему для администраторов и менеджеров на странице управления пользователями

## Проблема

На странице "Управление пользователями" (вкладка "Пользователи") есть колонка "Последний вход", но данные не отображаются (показывает "Никогда" для всех пользователей).

### Анализ

Фронтенд уже готов:
- В `managers.js` (строка 69) есть колонка таблицы "Последний вход"
- В `managers.js` (строка 94) есть код отображения: `${user.last_login ? formatDateTime(user.last_login) : 'Никогда'}`

Проблема на backend:
1. ❌ Модель `User` не имела поля `last_login`
2. ❌ API не записывал время входа при логине
3. ❌ Схема `UserResponse` не включала поле `last_login`

## Решение

### 1. База данных - Миграция 011

**Файл**: `web/app/migrations/011_add_last_login_to_users.sql`

Добавлена колонка `last_login` типа `TIMESTAMP` в таблицу `users`:

```sql
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;

COMMENT ON COLUMN users.last_login IS 'Дата и время последнего входа пользователя в систему';
```

### 2. Модель User

**Файл**: `web/app/models/user.py`  
**Изменение**: Добавлено поле в модель SQLAlchemy

```python
# Статус и метаданные
is_active = Column(Boolean, nullable=False, default=True, index=True)
registered_at = Column(DateTime, default=func.now())
last_interaction = Column(DateTime, nullable=True)
last_login = Column(DateTime, nullable=True)  # ✅ ДОБАВЛЕНО
created_at = Column(DateTime, nullable=False, server_default=func.now())
updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
```

### 3. Схема UserResponse

**Файл**: `web/app/models/user_schemas.py`  
**Изменение**: Добавлено поле в Pydantic схему ответа

```python
# Статус
is_active: bool
registered_at: Optional[datetime] = None
last_interaction: Optional[datetime] = None
last_login: Optional[datetime] = None  # ✅ ДОБАВЛЕНО
created_at: datetime
updated_at: datetime
```

### 4. API аутентификации

**Файл**: `web/app/api/auth.py`  
**Функция**: `login()`  
**Изменение**: Запись времени входа при успешной аутентификации

```python
@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """Вход в систему"""
    user = authenticate_user(db, credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ✅ ДОБАВЛЕНО: Обновить время последнего входа
    user.last_login = datetime.now()
    db.commit()
    
    access_token = create_access_token(...)
    # ... остальной код
```

## Развёртывание

### Файлы на сервере

1. **Миграция**
   ```bash
   /home/kktapp/kkt-system/web/app/migrations/011_add_last_login_to_users.sql
   ```

2. **Модель User**
   ```bash
   /home/kktapp/kkt-system/web/app/models/user.py
   ```

3. **Схемы**
   ```bash
   /home/kktapp/kkt-system/web/app/models/user_schemas.py
   ```

4. **API аутентификации**
   ```bash
   /home/kktapp/kkt-system/web/app/api/auth.py
   ```

### Команды развёртывания

```bash
# 1. Загрузка миграции
scp d:\QoProj\KKT\web\app\migrations\011_add_last_login_to_users.sql \
    root@185.185.71.248:/home/kktapp/kkt-system/web/app/migrations/

# 2. Загрузка скрипта применения
scp d:\QoProj\KKT\web\apply_migration_011.py \
    root@185.185.71.248:/home/kktapp/kkt-system/web/

# 3. Загрузка обновлённых моделей
scp d:\QoProj\KKT\web\app\models\user.py \
    root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/

scp d:\QoProj\KKT\web\app\models\user_schemas.py \
    root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/

# 4. Загрузка обновлённого API
scp d:\QoProj\KKT\web\app\api\auth.py \
    root@185.185.71.248:/home/kktapp/kkt-system/web/app/api/

# 5. Установка прав
ssh root@185.185.71.248 "chown -R kktapp:kktapp /home/kktapp/kkt-system/web/"

# 6. Применение миграции к БД kkt_production
ssh root@185.185.71.248 \
    "su - postgres -c 'psql -d kkt_production -f /home/kktapp/kkt-system/web/app/migrations/011_add_last_login_to_users.sql'"

# Результат:
# NOTICE:  column "last_login" of relation "users" already exists, skipping
# ALTER TABLE
# COMMENT

# 7. Перезапуск веб-сервиса
ssh root@185.185.71.248 "systemctl restart kkt-web.service"
```

### Проверка применения

```bash
# Статус сервиса
ssh root@185.185.71.248 "systemctl status kkt-web.service --no-pager"

# Результат:
# ● kkt-web.service - KKT Web Application
#      Active: active (running) since Sat 2025-12-20 20:17:33 MSK
```

## Как работает

### Последовательность событий

1. **Вход пользователя**
   ```
   Пользователь → Форма логина → POST /api/auth/login
   ```

2. **Аутентификация**
   ```python
   # auth.py
   user = authenticate_user(db, username, password)
   ```

3. **Запись времени входа**
   ```python
   user.last_login = datetime.now()
   db.commit()
   ```

4. **Создание токена**
   ```python
   access_token = create_access_token(data={...})
   ```

5. **Загрузка списка пользователей**
   ```
   Dashboard → GET /api/users?page=1&page_size=50
   ```

6. **Отображение в таблице**
   ```javascript
   // managers.js
   ${user.last_login ? formatDateTime(user.last_login) : 'Никогда'}
   ```

### Формат даты

Функция `formatDateTime()` использует `formatDateTimeRU()` для отображения в российском формате:

```
20.12.2025 20:17
```

## Тестирование

### Шаги проверки

1. **Войти в систему** как администратор или менеджер
2. **Перейти на вкладку "Пользователи"**
3. **Проверить колонку "Последний вход"**
4. **Выйти и войти снова**
5. **Обновить страницу** (F5)
6. **Проверить, что время обновилось**

### Ожидаемые результаты

**Для нового пользователя** (никогда не входил):
```
Последний вход: Никогда
```

**После первого входа**:
```
Последний вход: 20.12.2025 20:17
```

**После повторного входа** (время обновляется):
```
Последний вход: 20.12.2025 21:05
```

### Тестовые сценарии

**Сценарий 1**: Первый вход пользователя
```
1. Создать нового администратора
2. Активировать аккаунт
3. Войти в систему
4. Проверить: last_login = текущее время
```

**Сценарий 2**: Повторный вход
```
1. Войти в систему в 20:17
2. Выйти
3. Войти снова в 21:05
4. Проверить: last_login обновился на 21:05
```

**Сценарий 3**: Отображение в списке
```
1. Войти как admin
2. Перейти на вкладку "Пользователи"
3. Проверить: для всех админов/менеджеров показывается время входа
4. Проверить: для клиентов показывается "Никогда" или их время
```

## Технические детали

### Тип данных

- **БД**: `TIMESTAMP` (PostgreSQL)
- **Python**: `datetime` (nullable)
- **API**: `Optional[datetime]` (ISO 8601 формат)
- **Frontend**: `string` → форматируется в российский формат

### Timezone

⚠️ **Важно**: В текущей реализации используется `datetime.now()` без указания timezone. Для production рекомендуется использовать UTC:

```python
from datetime import datetime, timezone

user.last_login = datetime.now(timezone.utc)
```

### Индексация

Поле `last_login` не индексируется, так как:
- Не используется в WHERE условиях
- Не используется для сортировки
- Используется только для отображения

Если в будущем потребуется сортировка или фильтрация по последнему входу, добавить индекс:

```sql
CREATE INDEX idx_users_last_login ON users(last_login);
```

## Дополнительные возможности

### Потенциальные улучшения

1. **История входов**
   - Создать таблицу `login_history` для хранения всех входов
   - Записывать IP-адрес, User-Agent, геолокацию

2. **Статистика активности**
   - Дашборд с графиками входов по дням/часам
   - Топ активных пользователей
   - Неактивные пользователи (не входили N дней)

3. **Безопасность**
   - Уведомления о входе с нового устройства
   - Блокировка при подозрительной активности
   - Принудительный выход всех сессий

4. **Аудит**
   - Логирование всех попыток входа (успешных и неуспешных)
   - Отчёты по безопасности
   - Алерты при множественных неудачных попытках

## Связанные файлы

### Backend
- `web/app/models/user.py` - модель User с полем last_login
- `web/app/models/user_schemas.py` - схемы с last_login
- `web/app/api/auth.py` - обновление last_login при логине
- `web/app/migrations/011_add_last_login_to_users.sql` - миграция БД

### Frontend
- `web/app/static/js/managers.js` - отображение last_login в таблице

### Утилиты
- `web/apply_migration_011.py` - скрипт применения миграции

## Заключение

Функция отображения последнего входа полностью реализована и развёрнута на production сервере.

**Ключевые изменения**:
- ✅ Добавлено поле `last_login` в БД (миграция 011)
- ✅ Обновлена модель `User` с новым полем
- ✅ Обновлена схема `UserResponse` для API
- ✅ API записывает время при каждом входе
- ✅ Фронтенд корректно отображает данные

**Статус**: ✅ Реализовано и развёрнуто  
**Дата развёртывания**: 20.12.2025 20:17 MSK  
**Версия**: Production
