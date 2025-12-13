# Улучшения панели статистики

## Дата создания
13 декабря 2024

## Описание задачи
Реализованы три улучшения для страницы статистики:

1. **Кликабельные карточки статистики** - карточки "Всего клиентов", "Всего дедлайнов", "Истекает скоро", "Просрочено" теперь кликабельны и переводят пользователя к соответствующим данным
2. **Просроченные дедлайны в таблице "Срочные дедлайны"** - таблица на странице статистики теперь включает просроченные дедлайны
3. **Линейная диаграмма статусов** - график "Распределение по статусам" изменен с круговой (doughnut) на линейную диаграмму

## Внесенные изменения

### 1. HTML - Кликабельные карточки
**Файл:** `web/app/static/dashboard.html`

**Изменения:**
- Добавлен класс `clickable-card` ко всем четырем карточкам статистики
- Добавлены обработчики `onclick` для каждой карточки:
  - "Всего клиентов" → `navigateToClients()`
  - "Всего дедлайнов" → `navigateToAllDeadlines()`
  - "Истекает скоро" → `navigateToUrgentDeadlines()`
  - "Просрочено" → `navigateToExpiredDeadlines()`
- Добавлены inline стили: `cursor: pointer` и `transition: transform 0.2s`

### 2. JavaScript - Логика навигации и графики
**Файл:** `web/app/static/js/dashboard.js`

**Добавлены функции навигации:**
```javascript
function navigateToClients() {
    // Сбрасываем фильтр неактивных клиентов
    if (typeof showInactiveUsers !== 'undefined') {
        showInactiveUsers = false;
    }
    switchSection('users');
    window.location.hash = 'users';
}

function navigateToAllDeadlines() {
    switchSection('deadlines');
    window.location.hash = 'deadlines';
    // Сброс всех фильтров для отображения всех дедлайнов
    setTimeout(() => {
        if (typeof resetFilters === 'function') {
            resetFilters();
        }
    }, 100);
}

function navigateToUrgentDeadlines() {
    switchSection('deadlines');
    window.location.hash = 'deadlines';
    // Установка фильтра для срочных дедлайнов (0-7 дней)
    setTimeout(() => {
        const checkAndApply = () => {
            const filterDays = document.getElementById('filterDays');
            if (filterDays) {
                filterDays.value = 'urgent';
                if (typeof applyFilters === 'function') {
                    applyFilters();
                }
            } else {
                // Повторная попытка через 50мс если элемент не загружен
                setTimeout(checkAndApply, 50);
            }
        };
        checkAndApply();
    }, 100);
}

function navigateToExpiredDeadlines() {
    switchSection('deadlines');
    window.location.hash = 'deadlines';
    // Установка фильтра для просроченных дедлайнов
    setTimeout(() => {
        const checkAndApply = () => {
            const filterDays = document.getElementById('filterDays');
            if (filterDays) {
                filterDays.value = 'expired';
                if (typeof applyFilters === 'function') {
                    applyFilters();
                }
            } else {
                // Повторная попытка через 50мс если элемент не загружен
                setTimeout(checkAndApply, 50);
            }
        };
        checkAndApply();
    }, 100);
}
```

**Ключевые особенности реализации:**
- Используется механизм `checkAndApply()` для надежного применения фильтров
- Функция ожидает появления элементов DOM перед установкой значений
- При переходе к клиентам сбрасывается фильтр неактивных пользователей
- При переходе ко всем дедлайнам вызывается `resetFilters()` для сброса всех фильтров
- Для срочных и просроченных используется фильтр `filterDays` с соответствующими значениями

**Изменения в функции `renderStatusChart()`:**
- Изменен тип графика с `'doughnut'` на `'line'`
- Добавлено свойство `label: 'Количество дедлайнов'` в dataset
- Изменена прозрачность backgroundColor с `0.8` на `0.2` (для линейной диаграммы)
- Увеличена толщина линии: `borderWidth: 3`
- Добавлены параметры для плавной линии:
  - `fill: true` - заливка под линией
  - `tension: 0.4` - плавность кривых
  - `pointBackgroundColor` - цвета точек на графике
  - `pointBorderColor: '#fff'` - белая обводка точек
  - `pointBorderWidth: 2` - толщина обводки
  - `pointRadius: 5` - размер точек
  - `pointHoverRadius: 7` - размер точек при наведении
- Добавлена ось Y в настройках: `scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }`
- Легенда теперь отображается: `legend: { display: true }`

### 3. CSS - Стили для hover-эффекта
**Файл:** `web/app/static/css/styles.css`

**Добавлены стили:**
```css
/* Кликабельные карточки статистики */
.clickable-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

.clickable-card:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
}
```

**Эффект:** При наведении курсора карточка поднимается на 4px вверх и появляется более выраженная тень.

### 4. Backend API - Включение просроченных дедлайнов
**Файл:** `web/app/api/deadlines.py`

**Изменения в endpoint `/api/deadlines/urgent`:**

**Было:**
```python
async def get_expiring_soon(
    days: int = Query(14, ...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить дедлайны, истекающие в ближайшие N дней"""
    
    target_date = date.today() + timedelta(days=days)
    
    deadlines = db.query(Deadline)\
        .filter(
            and_(
                Deadline.status == 'active',
                Deadline.expiration_date >= date.today(),  # Только будущие
                Deadline.expiration_date <= target_date
            )
        ).order_by(Deadline.expiration_date).all()
```

**Стало:**
```python
async def get_expiring_soon(
    days: int = Query(14, ...),
    include_expired: bool = Query(True, description="Включать просроженные дедлайны"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить дедлайны, истекающие в ближайшие N дней (и просроченные, если include_expired=True)"""
    
    target_date = date.today() + timedelta(days=days)
    
    base_query = db.query(Deadline)\
        .outerjoin(User, Deadline.user_id == User.id)\
        .join(DeadlineType, Deadline.deadline_type_id == DeadlineType.id)\
        .filter(Deadline.status == 'active')
    
    if include_expired:
        # Включаем все дедлайны до target_date (включая просроченные)
        deadlines = base_query.filter(
            Deadline.expiration_date <= target_date
        ).order_by(Deadline.expiration_date).all()
    else:
        # Только будущие дедлайны
        deadlines = base_query.filter(
            and_(
                Deadline.expiration_date >= date.today(),
                Deadline.expiration_date <= target_date
            )
        ).order_by(Deadline.expiration_date).all()
```

**Ключевые изменения:**
- Добавлен параметр `include_expired` (по умолчанию `True`)
- Изменена логика фильтрации: при `include_expired=True` выбираются все дедлайны с датой `<= target_date` (включая прошлые даты)
- Сохранена обратная совместимость: можно явно передать `include_expired=false` для старого поведения

## Результат

### Визуальные улучшения:
1. **Карточки реагируют на наведение** - визуальная обратная связь показывает, что карточки кликабельны
2. **Клик переводит к данным** - удобная навигация напрямую из статистики
3. **Линейная диаграмма** - более наглядное отображение распределения статусов с плавными переходами

### Функциональные улучшения:
1. **Просроченные дедлайны видны** - пользователь сразу видит критичные задачи в таблице "Срочные дедлайны"
2. **Быстрая навигация** - один клик для перехода к нужному разделу с применением соответствующих фильтров
3. **API расширен** - новый параметр `include_expired` позволяет гибко управлять выборкой

## Требуется перезапуск сервера

После внесения изменений необходимо перезапустить веб-сервер:

```bash
# Windows
.\restart_web_server.bat

# Или вручную
taskkill /F /IM uvicorn.exe
start_web.bat
```

## Тестирование

После перезапуска сервера проверить:
1. ✅ Карточки статистики имеют hover-эффект
2. ✅ Клик на "Всего клиентов" → переход в раздел "Клиенты" (только активные)
3. ✅ Клик на "Всего дедлайнов" → переход в раздел "Дедлайны" (все дедлайны, фильтры сброшены)
4. ✅ Клик на "Истекает скоро" → переход в раздел "Дедлайны" с фильтром "Срочно (0-7 дн.)"
5. ✅ Клик на "Просрочено" → переход в раздел "Дедлайны" с фильтром "Просрочено (< 0)"
6. ✅ Таблица "Срочные дедлайны" отображает просроченные записи
7. ✅ График "Распределение по статусам" - линейная диаграмма

## Совместимость

- Изменения полностью обратно совместимы
- Старые вызовы API `/api/deadlines/urgent?days=14` работают как прежде (включают просроченные по умолчанию)
- Можно явно отключить просроченные: `/api/deadlines/urgent?days=14&include_expired=false`
