# Исправление сохранения адреса установки ККТ

## Проблема

При редактировании кассового аппарата (ККТ) в карточке клиента изменения адреса места установки не сохраняются в базе данных.

## Анализ причины

### Проверенные компоненты

| Компонент | Файл | Состояние | Описание |
|-----------|------|-----------|----------|
| База данных | `web/app/models/cash_register.py` | ✅ Корректно | Поле `installation_address` типа Text присутствует в модели CashRegister |
| API Backend Schema | `web/app/api/cash_registers.py` | ✅ Корректно | Схемы `CashRegisterCreate` и `CashRegisterUpdate` включают поле `installation_address` |
| API Backend Handler | `web/app/api/cash_registers.py` | ✅ Корректно | Метод `update_cash_register` корректно обрабатывает все поля через `data.dict(exclude_unset=True)` |
| Frontend Form | `web/app/static/js/client-details.js` | ✅ Корректно | Поле `installationAddress` читается из формы (строка 802) |
| Frontend Request Payload | `web/app/static/js/client-details.js` | ❌ ПРОБЛЕМА | Поле НЕ включено в объект data, отправляемый на сервер (строки 813-823) |

### Выявленная ошибка

В функции `saveRegister()` файла `client-details.js`:

**Строка 802**: значение адреса установки читается из формы
```javascript
const installationAddress = document.getElementById('installationAddress').value.trim();
```

**Строки 813-823**: формируется объект данных для отправки на сервер, НО поле `installation_address` отсутствует в объекте:
```javascript
const data = {
    client_id: clientData.id,
    register_name: registerName,
    model: registerModel,
    factory_number: serialNumber,
    fn_number: fiscalDriveNumber,
    ofd_provider_id: ofdProviderId ? parseInt(ofdProviderId) : null,
    notes: registerNotes || '',
    fn_expiry_date: fnReplacementDate,
    ofd_expiry_date: ofdRenewalDate
    // installation_address ОТСУТСТВУЕТ!
};
```

## Решение

### Требуемое изменение

Добавить поле `installation_address` в объект данных, формируемый в функции `saveRegister()`.

### Целевой файл

**Файл**: `web/app/static/js/client-details.js`  
**Функция**: `saveRegister()`  
**Строки**: 813-823

### Описание изменения

В объект `data` добавить свойство `installation_address` со значением переменной `installationAddress`:

```javascript
const data = {
    client_id: clientData.id,
    register_name: registerName,
    model: registerModel,
    factory_number: serialNumber,
    fn_number: fiscalDriveNumber,
    installation_address: installationAddress,  // ДОБАВИТЬ ЭТУ СТРОКУ
    ofd_provider_id: ofdProviderId ? parseInt(ofdProviderId) : null,
    notes: registerNotes || '',
    fn_expiry_date: fnReplacementDate,
    ofd_expiry_date: ofdRenewalDate
};
```

### Позиция вставки

Добавить строку `installation_address: installationAddress,` после строки `fn_number: fiscalDriveNumber,` (текущая строка 818).

## Ожидаемый результат

После внесения изменения:

1. При редактировании кассового аппарата значение поля "Адрес установки" будет передаваться в API
2. Backend корректно обработает поле и сохранит его в базе данных
3. При повторном открытии карточки ККТ сохранённый адрес установки будет отображаться

## Проверка исправления

### Шаги тестирования

1. Открыть карточку клиента с существующей кассой
2. Нажать "Редактировать" на карточке кассового аппарата
3. Изменить значение в поле "Адрес установки"
4. Сохранить изменения
5. Обновить страницу (F5)
6. Проверить, что новый адрес установки отображается в карточке кассы

### Критерии успеха

- Новое значение адреса установки сохраняется в базе данных
- После обновления страницы изменённый адрес отображается корректно
- В консоли браузера и логах сервера отсутствуют ошибки

## Связанная информация

### История проблемы

Ранее в проекте существовала проблема несоответствия контрактов данных между frontend и backend для полей `register_name` и `installation_address`. Эта проблема была решена через:

- Миграцию 010: добавление полей в таблицу `cash_registers`
- Обновление схем API в `cash_registers.py`
- Обновление модели БД в `cash_register.py`

Текущая проблема является остаточной ошибкой на уровне клиентского кода - поле было добавлено в форму и обработку на backend, но не было включено в payload запроса.

### Затронутые эндпоинты

- `PUT /cash-registers/{register_id}` - обновление кассового аппарата
- `POST /cash-registers` - создание кассового аппарата (также нуждается в проверке)

### Дополнительные проверки

После исправления рекомендуется также проверить функцию создания новой кассы, чтобы убедиться, что `installation_address` корректно передаётся и при создании новой записи.
