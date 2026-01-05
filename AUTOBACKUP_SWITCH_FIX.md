# Исправление визуального состояния переключателя автобэкапа

**Дата**: 20 декабря 2025  
**Задача**: Синхронизация визуального состояния MDL Switch с фактическим статусом автобэкапа

## Проблема

При загрузке страницы "Обслуживание БД" переключатель автоматических бэкапов визуально отображался в положении "выключено", хотя автобэкап был включён (показывал статус "✅ Автобэкап включён").

### Скриншот проблемы

Переключатель в положении "выключено", но текст статуса показывает "Автобэкап включён" (зелёная галочка).

## Причина

При программном изменении состояния checkbox (`enabledCheckbox.checked = schedule.enabled`) компонент Material Design Lite (MDL) не обновляет своё визуальное состояние автоматически. MDL Switch использует CSS-класс `is-checked` на родительском элементе `<label>` для отображения положения переключателя.

### Код с проблемой

```javascript
// database-management.js (строки 451-457)
function displayBackupSchedule(schedule) {
    const enabledCheckbox = document.getElementById('autoBackupEnabled');
    enabledCheckbox.checked = schedule.enabled;  // ✅ Изменяет состояние checkbox
    
    const settingsDiv = document.getElementById('autoBackupSettings');
    settingsDiv.style.display = schedule.enabled ? 'block' : 'none';
    // ❌ НЕ обновляет визуальное состояние MDL Switch
```

## Решение

Добавлен код для явного управления CSS-классом `is-checked` на родительском элементе переключателя.

### Внесённые изменения

**Файл**: `web/app/static/js/database-management.js`  
**Функция**: `displayBackupSchedule()`  
**Строки**: 451-465

```javascript
function displayBackupSchedule(schedule) {
    const enabledCheckbox = document.getElementById('autoBackupEnabled');
    enabledCheckbox.checked = schedule.enabled;
    
    // ✅ ДОБАВЛЕНО: Обновить визуальное состояние MDL переключателя
    const switchParent = enabledCheckbox.parentElement;
    if (schedule.enabled) {
        switchParent.classList.add('is-checked');
    } else {
        switchParent.classList.remove('is-checked');
    }
    
    const settingsDiv = document.getElementById('autoBackupSettings');
    settingsDiv.style.display = schedule.enabled ? 'block' : 'none';
    // ... остальной код
}
```

### Логика исправления

1. **Получаем родительский элемент** - `<label class="mdl-switch ...">` содержит checkbox
2. **Проверяем состояние** - если `schedule.enabled === true`
3. **Добавляем класс** - `switchParent.classList.add('is-checked')` - переключатель визуально включается
4. **Удаляем класс** - `switchParent.classList.remove('is-checked')` - переключатель визуально выключается

## Технические детали

### MDL Switch структура

```html
<label class="mdl-switch mdl-js-switch mdl-js-ripple-effect is-checked" for="autoBackupEnabled">
    <input type="checkbox" id="autoBackupEnabled" class="mdl-switch__input" checked>
    <span class="mdl-switch__label">Включить автоматические бэкапы</span>
</label>
```

- **Класс `is-checked`** на `<label>` управляет визуальным состоянием
- **Атрибут `checked`** на `<input>` управляет логическим состоянием
- Оба должны быть синхронизированы для корректного отображения

### Обновление версии файла

Для очистки кэша браузера обновлена версия JavaScript-файла в HTML:

```html
<!-- database-management.html (строка 296) -->
<script src="/static/js/database-management.js?v=20251220192800"></script>
```

Предыдущая версия: `v=20251220105400`  
Новая версия: `v=20251220192800`

## Развёртывание

### Загруженные файлы

1. **database-management.js**
   - Путь: `/home/kktapp/kkt-system/web/app/static/js/database-management.js`
   - Размер: 20KB
   - Права: `kktapp:kktapp`

2. **database-management.html**
   - Путь: `/home/kktapp/kkt-system/web/app/static/database-management.html`
   - Размер: ~12KB
   - Права: `kktapp:kktapp`

### Команды развёртывания

```bash
# 1. Загрузка JavaScript
scp "d:\QoProj\KKT\web\app\static\js\database-management.js" \
    root@185.185.71.248:/home/kktapp/kkt-system/web/app/static/js/

# 2. Загрузка HTML
scp "d:\QoProj\KKT\web\app\static\database-management.html" \
    root@185.185.71.248:/home/kktapp/kkt-system/web/app/static/

# 3. Установка прав
ssh root@185.185.71.248 \
    "chown kktapp:kktapp /home/kktapp/kkt-system/web/app/static/js/database-management.js && \
     chown kktapp:kktapp /home/kktapp/kkt-system/web/app/static/database-management.html"
```

## Проверка исправления

### Шаги тестирования

1. Открыть страницу "Обслуживание БД" в браузере
2. Очистить кэш браузера (Ctrl+F5 или Ctrl+Shift+R)
3. Проверить визуальное состояние переключателя "Включить автоматические бэкапы"
4. Сверить с текстом статуса под переключателем

### Критерии успеха

- ✅ Если автобэкап **включён** - переключатель в положении **вправо** (синий), статус "✅ Автобэкап включён"
- ✅ Если автобэкап **выключен** - переключатель в положении **влево** (серый), статус "⏸️ Автобэкап отключён"
- ✅ При переключении checkbox сразу изменяет визуальное состояние
- ✅ После сохранения настроек состояние сохраняется корректно

### Тестовые сценарии

**Сценарий 1**: Автобэкап включён
```
Ожидаемый результат:
- Переключатель: ВКЛ (синий, вправо)
- Статус: "✅ Автобэкап включён" (зелёный текст)
- Настройки: видимы
```

**Сценарий 2**: Автобэкап выключен
```
Ожидаемый результат:
- Переключатель: ВЫКЛ (серый, влево)
- Статус: "⏸️ Автобэкап отключён" (серый текст)
- Настройки: скрыты
```

**Сценарий 3**: Переключение состояния
```
Действие: Кликнуть на переключатель
Ожидаемый результат:
- Визуальное состояние сразу меняется
- Отправляется запрос на сервер
- Статус обновляется
- Настройки показываются/скрываются
```

## Связанные файлы

- `web/app/static/js/database-management.js` - основной JavaScript
- `web/app/static/database-management.html` - HTML страницы
- `web/app/api/database_management.py` - API для управления бэкапами

## Дополнительная информация

### MDL Switch API

MDL Switch компонент использует следующие методы для программного управления:

```javascript
// Получить MDL компонент
const switchElement = document.querySelector('.mdl-switch');
const switchComponent = switchElement.MaterialSwitch;

// Включить
switchComponent.on();

// Выключить
switchComponent.off();

// Альтернативный способ (используется в исправлении)
// Прямое управление классом
switchElement.classList.add('is-checked');    // Включить
switchElement.classList.remove('is-checked'); // Выключить
```

В данном исправлении использован прямой способ управления классом, так как он:
- Проще и понятнее
- Не требует доступа к MaterialSwitch API
- Работает надёжно для синхронизации состояния

## Заключение

Проблема полностью решена. Визуальное состояние переключателя автобэкапа теперь корректно синхронизируется с фактическим статусом при загрузке страницы.

**Статус**: ✅ Исправлено и развёрнуто  
**Версия**: 20251220192800  
**Затронутые компоненты**: Frontend (JS)
