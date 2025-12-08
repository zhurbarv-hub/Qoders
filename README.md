# СУБД для фиксации сроков истечения сервисов

## 📋 Описание

Полнофункциональная система управления базой данных для отслеживания сроков истечения сервисов, подписок и платежей. Система позволяет контролировать все ваши подписки, получать уведомления о приближающихся датах истечения и вести историю платежей.

## ✨ Возможности

- **Управление сервисами**: Добавление, редактирование и удаление информации о сервисах
- **Управление подписками**: Отслеживание дат начала, истечения и продления подписок
- **История платежей**: Ведение полной истории всех платежей по подпискам
- **Уведомления**: Автоматическая генерация уведомлений о приближающихся сроках истечения
- **Статистика**: Подробная статистика по сервисам, подпискам и платежам
- **Экспорт данных**: Экспорт всех данных в формате JSON

## 📁 Структура проекта

```
KKT/
├── schema.sql           # SQL схема базы данных
├── service_tracker.py   # Основной модуль работы с БД
├── example_usage.py     # Примеры использования и демонстрация
├── requirements.txt     # Зависимости проекта
└── README.md           # Документация
```

## 🗄️ Структура базы данных

### Таблицы:

1. **services** - Информация о сервисах
   - id, service_name, description, provider, category, cost, currency, created_at, updated_at, is_active

2. **subscriptions** - Подписки на сервисы
   - id, service_id, subscription_type, start_date, expiration_date, renewal_date, auto_renewal, notification_days, status, notes

3. **payment_history** - История платежей
   - id, subscription_id, payment_date, amount, currency, payment_method, transaction_id, status, notes

4. **notifications** - Уведомления
   - id, subscription_id, notification_date, notification_type, is_sent, sent_at, message

### Представления (Views):

- **v_active_subscriptions** - Активные подписки с полной информацией
- **v_expiring_subscriptions** - Истекающие подписки
- **v_payment_statistics** - Статистика по платежам

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

(SQLite3 уже включен в стандартную библиотеку Python)

### 2. Запуск демонстрации

```bash
python example_usage.py
```

Это запустит полную демонстрацию возможностей системы.

### 3. Использование в коде

```python
from service_tracker import ServiceTracker

# Создание экземпляра трекера
with ServiceTracker("services.db") as tracker:
    
    # Добавление сервиса
    service_id = tracker.add_service(
        service_name="Netflix",
        description="Стриминговый сервис",
        provider="Netflix Inc.",
        category="Развлечения",
        cost=799.00,
        currency="RUB"
    )
    
    # Добавление подписки
    subscription_id = tracker.add_subscription(
        service_id=service_id,
        start_date="2024-01-01",
        expiration_date="2025-01-01",
        subscription_type="yearly",
        auto_renewal=True,
        notification_days=30
    )
    
    # Получение истекающих подписок
    expiring = tracker.get_expiring_subscriptions(days=30)
    for sub in expiring:
        print(f"{sub['service_name']} истекает {sub['expiration_date']}")
    
    # Добавление платежа
    payment_id = tracker.add_payment(
        subscription_id=subscription_id,
        payment_date="2024-01-01",
        amount=799.00,
        currency="RUB",
        payment_method="Банковская карта"
    )
    
    # Генерация уведомлений
    tracker.generate_notifications_for_expiring_subscriptions()
    
    # Получение статистики
    stats = tracker.get_statistics()
    print(f"Активных подписок: {stats['active_subscriptions']}")
```

## 📊 Основные методы API

### Работа с сервисами:

- `add_service(service_name, description, provider, category, cost, currency)` - Добавить сервис
- `get_service(service_id)` - Получить сервис по ID
- `get_all_services(active_only=True)` - Получить все сервисы
- `update_service(service_id, **kwargs)` - Обновить сервис
- `delete_service(service_id)` - Удалить сервис (мягкое удаление)

### Работа с подписками:

- `add_subscription(service_id, start_date, expiration_date, ...)` - Добавить подписку
- `get_subscription(subscription_id)` - Получить подписку
- `get_active_subscriptions()` - Получить активные подписки
- `get_expiring_subscriptions(days=None)` - Получить истекающие подписки
- `update_subscription(subscription_id, **kwargs)` - Обновить подписку
- `renew_subscription(subscription_id, new_expiration_date)` - Продлить подписку
- `cancel_subscription(subscription_id)` - Отменить подписку

### Работа с платежами:

- `add_payment(subscription_id, payment_date, amount, ...)` - Добавить платеж
- `get_payment_history(subscription_id=None)` - Получить историю платежей
- `get_payment_statistics()` - Получить статистику по платежам

### Работа с уведомлениями:

- `create_notification(subscription_id, notification_date, notification_type, message)` - Создать уведомление
- `get_pending_notifications()` - Получить неотправленные уведомления
- `mark_notification_sent(notification_id)` - Отметить уведомление как отправленное

### Утилиты:

- `check_and_update_expired_subscriptions()` - Проверить и обновить истекшие подписки
- `generate_notifications_for_expiring_subscriptions()` - Генерировать уведомления
- `get_statistics()` - Получить общую статистику
- `export_to_json(filepath)` - Экспортировать данные в JSON

## 💡 Примеры использования

### Проверка истекающих подписок

```python
with ServiceTracker() as tracker:
    expiring = tracker.get_expiring_subscriptions(days=7)
    for sub in expiring:
        print(f"⚠️ {sub['service_name']} истекает через {sub['days_until_expiration']} дней")
```

### Продление подписки

```python
from datetime import datetime, timedelta

with ServiceTracker() as tracker:
    new_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    tracker.renew_subscription(subscription_id=1, new_expiration_date=new_date)
```

### Получение статистики

```python
with ServiceTracker() as tracker:
    stats = tracker.get_statistics()
    print(f"Активных сервисов: {stats['active_services']}")
    print(f"Активных подписок: {stats['active_subscriptions']}")
    print(f"Сумма платежей: {stats['total_payments']:.2f}")
```

## 🔧 Автоматизация

Для автоматической проверки истекающих подписок можно настроить периодический запуск:

```python
# check_subscriptions.py
from service_tracker import ServiceTracker

with ServiceTracker() as tracker:
    # Обновляем статус истекших подписок
    tracker.check_and_update_expired_subscriptions()
    
    # Генерируем уведомления
    count = tracker.generate_notifications_for_expiring_subscriptions()
    print(f"Создано уведомлений: {count}")
    
    # Получаем неотправленные уведомления
    notifications = tracker.get_pending_notifications()
    for notif in notifications:
        print(notif['message'])
        # Здесь можно отправить email, Telegram сообщение и т.д.
        tracker.mark_notification_sent(notif['id'])
```

Добавьте этот скрипт в планировщик задач (Windows) или cron (Linux) для ежедневного запуска.

## 📈 Расширение функционала

Систему можно легко расширить:

- Добавить отправку email/Telegram уведомлений
- Интегрировать с платежными системами
- Создать веб-интерфейс (Flask/Django)
- Добавить поддержку нескольких валют с конвертацией
- Реализовать отчеты и графики
- Добавить категории расходов и бюджетирование

## 📝 Лицензия

Свободное использование для личных и коммерческих целей.

## 👨‍💻 Автор

Создано с помощью Qoder AI

---

**Примечание:** Для работы требуется Python 3.6 или выше. База данных SQLite создается автоматически при первом запуске.
