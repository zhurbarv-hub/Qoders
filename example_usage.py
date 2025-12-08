"""
Пример использования СУБД для фиксации сроков истечения сервисов
"""

from service_tracker import ServiceTracker
from datetime import datetime, timedelta
import sys


def print_separator():
    """Печатает разделитель"""
    print("\n" + "="*80 + "\n")


def demonstrate_basic_operations():
    """Демонстрация базовых операций с сервисами и подписками"""
    
    print("📋 ДЕМОНСТРАЦИЯ РАБОТЫ СИСТЕМЫ ОТСЛЕЖИВАНИЯ СЕРВИСОВ")
    print_separator()
    
    # Создаем экземпляр трекера
    with ServiceTracker("services.db") as tracker:
        
        # ============ ДОБАВЛЕНИЕ СЕРВИСОВ ============
        print("1️⃣ ДОБАВЛЕНИЕ СЕРВИСОВ")
        print("-" * 80)
        
        try:
            # Добавляем несколько сервисов
            service1_id = tracker.add_service(
                service_name="Netflix",
                description="Стриминговый сервис фильмов и сериалов",
                provider="Netflix Inc.",
                category="Развлечения",
                cost=799.00,
                currency="RUB"
            )
            print(f"✅ Добавлен сервис: Netflix (ID: {service1_id})")
            
            service2_id = tracker.add_service(
                service_name="GitHub Pro",
                description="Профессиональная подписка GitHub",
                provider="GitHub",
                category="Разработка",
                cost=4.00,
                currency="USD"
            )
            print(f"✅ Добавлен сервис: GitHub Pro (ID: {service2_id})")
            
            service3_id = tracker.add_service(
                service_name="Spotify Premium",
                description="Музыкальный стриминговый сервис",
                provider="Spotify AB",
                category="Музыка",
                cost=169.00,
                currency="RUB"
            )
            print(f"✅ Добавлен сервис: Spotify Premium (ID: {service3_id})")
            
            service4_id = tracker.add_service(
                service_name="Adobe Creative Cloud",
                description="Подписка на пакет Adobe",
                provider="Adobe Inc.",
                category="Графика",
                cost=2990.00,
                currency="RUB"
            )
            print(f"✅ Добавлен сервис: Adobe Creative Cloud (ID: {service4_id})")
            
        except ValueError as e:
            print(f"⚠️ Сервисы уже добавлены ранее")
        
        print_separator()
        
        # ============ ПРОСМОТР ВСЕХ СЕРВИСОВ ============
        print("2️⃣ СПИСОК ВСЕХ СЕРВИСОВ")
        print("-" * 80)
        
        services = tracker.get_all_services()
        for service in services:
            print(f"ID: {service['id']:2d} | {service['service_name']:25s} | "
                  f"Категория: {service['category']:15s} | "
                  f"Цена: {service['cost']:8.2f} {service['currency']}")
        
        print_separator()
        
        # ============ ДОБАВЛЕНИЕ ПОДПИСОК ============
        print("3️⃣ ДОБАВЛЕНИЕ ПОДПИСОК")
        print("-" * 80)
        
        # Текущая дата
        today = datetime.now().date()
        
        # Добавляем подписки на сервисы
        subscriptions_data = [
            {
                'service_id': 1,
                'start_date': (today - timedelta(days=180)).strftime('%Y-%m-%d'),
                'expiration_date': (today + timedelta(days=15)).strftime('%Y-%m-%d'),
                'subscription_type': 'monthly',
                'auto_renewal': True,
                'notification_days': 7
            },
            {
                'service_id': 2,
                'start_date': (today - timedelta(days=300)).strftime('%Y-%m-%d'),
                'expiration_date': (today + timedelta(days=65)).strftime('%Y-%m-%d'),
                'subscription_type': 'yearly',
                'auto_renewal': True,
                'notification_days': 30
            },
            {
                'service_id': 3,
                'start_date': (today - timedelta(days=25)).strftime('%Y-%m-%d'),
                'expiration_date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
                'subscription_type': 'monthly',
                'auto_renewal': False,
                'notification_days': 7
            },
            {
                'service_id': 4,
                'start_date': (today - timedelta(days=330)).strftime('%Y-%m-%d'),
                'expiration_date': (today + timedelta(days=35)).strftime('%Y-%m-%d'),
                'subscription_type': 'yearly',
                'auto_renewal': True,
                'notification_days': 60
            }
        ]
        
        for sub_data in subscriptions_data:
            sub_id = tracker.add_subscription(**sub_data)
            service = tracker.get_service(sub_data['service_id'])
            print(f"✅ Создана подписка на '{service['service_name']}' "
                  f"(истекает: {sub_data['expiration_date']})")
        
        print_separator()
        
        # ============ АКТИВНЫЕ ПОДПИСКИ ============
        print("4️⃣ АКТИВНЫЕ ПОДПИСКИ")
        print("-" * 80)
        
        active_subs = tracker.get_active_subscriptions()
        for sub in active_subs:
            days_left = sub['days_until_expiration']
            status_icon = "🔴" if days_left <= 7 else "🟡" if days_left <= 30 else "🟢"
            auto_renew_icon = "🔄" if sub['auto_renewal'] else "❌"
            
            print(f"{status_icon} {sub['service_name']:25s} | "
                  f"Истекает: {sub['expiration_date']:10s} | "
                  f"Осталось дней: {days_left:3d} | "
                  f"Автопродление: {auto_renew_icon}")
        
        print_separator()
        
        # ============ ИСТЕКАЮЩИЕ ПОДПИСКИ ============
        print("5️⃣ ИСТЕКАЮЩИЕ ПОДПИСКИ (следующие 30 дней)")
        print("-" * 80)
        
        expiring_subs = tracker.get_expiring_subscriptions(days=30)
        if expiring_subs:
            for sub in expiring_subs:
                days_left = sub['days_until_expiration']
                urgency = "СРОЧНО!" if days_left <= 7 else "Скоро"
                print(f"⚠️ [{urgency:8s}] {sub['service_name']:25s} | "
                      f"Истекает: {sub['expiration_date']} | "
                      f"Осталось: {days_left} дн.")
        else:
            print("✅ Нет истекающих подписок")
        
        print_separator()
        
        # ============ ДОБАВЛЕНИЕ ПЛАТЕЖЕЙ ============
        print("6️⃣ ДОБАВЛЕНИЕ ПЛАТЕЖЕЙ")
        print("-" * 80)
        
        # Добавляем платежи для некоторых подписок
        payments_data = [
            {
                'subscription_id': 1,
                'payment_date': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
                'amount': 799.00,
                'currency': 'RUB',
                'payment_method': 'Банковская карта',
                'transaction_id': 'TXN-001-2024'
            },
            {
                'subscription_id': 2,
                'payment_date': (today - timedelta(days=300)).strftime('%Y-%m-%d'),
                'amount': 48.00,
                'currency': 'USD',
                'payment_method': 'PayPal',
                'transaction_id': 'TXN-002-2024'
            },
            {
                'subscription_id': 3,
                'payment_date': (today - timedelta(days=25)).strftime('%Y-%m-%d'),
                'amount': 169.00,
                'currency': 'RUB',
                'payment_method': 'Банковская карта',
                'transaction_id': 'TXN-003-2024'
            }
        ]
        
        for payment in payments_data:
            payment_id = tracker.add_payment(**payment)
            print(f"✅ Платеж #{payment_id}: {payment['amount']} {payment['currency']} "
                  f"({payment['payment_date']})")
        
        print_separator()
        
        # ============ СТАТИСТИКА ПЛАТЕЖЕЙ ============
        print("7️⃣ СТАТИСТИКА ПО ПЛАТЕЖАМ")
        print("-" * 80)
        
        payment_stats = tracker.get_payment_statistics()
        total_rub = 0
        for stat in payment_stats:
            print(f"📊 {stat['service_name']:25s} | "
                  f"Платежей: {stat['payment_count']:2d} | "
                  f"Всего: {stat['total_paid']:8.2f} | "
                  f"Средний чек: {stat['average_payment']:8.2f}")
        
        print_separator()
        
        # ============ ГЕНЕРАЦИЯ УВЕДОМЛЕНИЙ ============
        print("8️⃣ ГЕНЕРАЦИЯ УВЕДОМЛЕНИЙ")
        print("-" * 80)
        
        notifications_count = tracker.generate_notifications_for_expiring_subscriptions()
        print(f"✅ Создано уведомлений: {notifications_count}")
        
        # Получаем неотправленные уведомления
        pending_notifications = tracker.get_pending_notifications()
        if pending_notifications:
            print("\nНеотправленные уведомления:")
            for notif in pending_notifications:
                print(f"  📧 {notif['message']}")
        
        print_separator()
        
        # ============ ПРОВЕРКА ИСТЕКШИХ ПОДПИСОК ============
        print("9️⃣ ПРОВЕРКА ИСТЕКШИХ ПОДПИСОК")
        print("-" * 80)
        
        expired_count = tracker.check_and_update_expired_subscriptions()
        print(f"✅ Обновлено истекших подписок: {expired_count}")
        
        print_separator()
        
        # ============ ОБЩАЯ СТАТИСТИКА ============
        print("🔟 ОБЩАЯ СТАТИСТИКА СИСТЕМЫ")
        print("-" * 80)
        
        stats = tracker.get_statistics()
        print(f"📌 Активных сервисов: {stats['active_services']}")
        print(f"📌 Активных подписок: {stats['active_subscriptions']}")
        print(f"📌 Истекающих подписок: {stats['expiring_subscriptions']}")
        print(f"📌 Сумма всех платежей: {stats['total_payments']:.2f}")
        print(f"📌 Ожидающих уведомлений: {stats['pending_notifications']}")
        
        print_separator()
        
        # ============ ЭКСПОРТ В JSON ============
        print("💾 ЭКСПОРТ ДАННЫХ В JSON")
        print("-" * 80)
        
        tracker.export_to_json("services_export.json")
        print("✅ Данные экспортированы в файл: services_export.json")
        
        print_separator()
        print("✨ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ✨")


def demonstrate_subscription_management():
    """Демонстрация управления подписками"""
    
    print("\n🔧 УПРАВЛЕНИЕ ПОДПИСКАМИ")
    print_separator()
    
    with ServiceTracker("services.db") as tracker:
        
        # Продление подписки
        print("📅 ПРОДЛЕНИЕ ПОДПИСКИ")
        print("-" * 80)
        
        # Получаем первую подписку
        subscriptions = tracker.get_active_subscriptions()
        if subscriptions:
            sub = subscriptions[0]
            new_expiration = (datetime.now().date() + timedelta(days=365)).strftime('%Y-%m-%d')
            
            success = tracker.renew_subscription(
                subscription_id=sub['subscription_id'],
                new_expiration_date=new_expiration
            )
            
            if success:
                print(f"✅ Подписка на '{sub['service_name']}' продлена до {new_expiration}")
        
        print_separator()
        
        # Обновление информации о сервисе
        print("✏️ ОБНОВЛЕНИЕ ИНФОРМАЦИИ О СЕРВИСЕ")
        print("-" * 80)
        
        services = tracker.get_all_services()
        if services:
            service = services[0]
            success = tracker.update_service(
                service_id=service['id'],
                cost=899.00,
                description=f"{service['description']} (обновлено)"
            )
            
            if success:
                updated_service = tracker.get_service(service['id'])
                print(f"✅ Сервис '{service['service_name']}' обновлен")
                print(f"   Новая цена: {updated_service['cost']} {updated_service['currency']}")
        
        print_separator()


def interactive_menu():
    """Интерактивное меню для работы с системой"""
    
    tracker = ServiceTracker("services.db")
    
    while True:
        print("\n" + "="*80)
        print("📋 МЕНЮ УПРАВЛЕНИЯ СЕРВИСАМИ")
        print("="*80)
        print("1. Показать все сервисы")
        print("2. Добавить новый сервис")
        print("3. Показать активные подписки")
        print("4. Показать истекающие подписки")
        print("5. Добавить подписку")
        print("6. Показать статистику")
        print("7. Экспортировать данные")
        print("0. Выход")
        print("="*80)
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == '1':
            services = tracker.get_all_services()
            print("\n📋 СПИСОК СЕРВИСОВ:")
            for s in services:
                print(f"  {s['id']:2d}. {s['service_name']:30s} - {s['cost']:8.2f} {s['currency']}")
        
        elif choice == '2':
            print("\n➕ ДОБАВЛЕНИЕ НОВОГО СЕРВИСА:")
            name = input("Название: ")
            description = input("Описание: ")
            provider = input("Поставщик: ")
            category = input("Категория: ")
            cost = float(input("Цена: "))
            currency = input("Валюта (RUB): ") or "RUB"
            
            try:
                service_id = tracker.add_service(name, description, provider, category, cost, currency)
                print(f"✅ Сервис добавлен с ID: {service_id}")
            except ValueError as e:
                print(f"❌ Ошибка: {e}")
        
        elif choice == '3':
            subs = tracker.get_active_subscriptions()
            print("\n📋 АКТИВНЫЕ ПОДПИСКИ:")
            for s in subs:
                print(f"  {s['service_name']:30s} - истекает {s['expiration_date']} "
                      f"(через {s['days_until_expiration']} дн.)")
        
        elif choice == '4':
            subs = tracker.get_expiring_subscriptions()
            print("\n⚠️ ИСТЕКАЮЩИЕ ПОДПИСКИ:")
            for s in subs:
                print(f"  {s['service_name']:30s} - {s['expiration_date']} "
                      f"(осталось {s['days_until_expiration']} дн.)")
        
        elif choice == '5':
            print("\n➕ ДОБАВЛЕНИЕ ПОДПИСКИ:")
            service_id = int(input("ID сервиса: "))
            start_date = input("Дата начала (YYYY-MM-DD): ")
            expiration_date = input("Дата истечения (YYYY-MM-DD): ")
            subscription_type = input("Тип (monthly/yearly): ")
            
            sub_id = tracker.add_subscription(service_id, start_date, expiration_date, subscription_type)
            print(f"✅ Подписка создана с ID: {sub_id}")
        
        elif choice == '6':
            stats = tracker.get_statistics()
            print("\n📊 СТАТИСТИКА:")
            print(f"  Активных сервисов: {stats['active_services']}")
            print(f"  Активных подписок: {stats['active_subscriptions']}")
            print(f"  Истекающих подписок: {stats['expiring_subscriptions']}")
            print(f"  Сумма платежей: {stats['total_payments']:.2f}")
        
        elif choice == '7':
            filename = input("Имя файла для экспорта (services_export.json): ") or "services_export.json"
            tracker.export_to_json(filename)
            print(f"✅ Данные экспортированы в {filename}")
        
        elif choice == '0':
            print("\n👋 До свидания!")
            tracker.close()
            break
        
        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║             СУБД ДЛЯ ФИКСАЦИИ СРОКОВ ИСТЕЧЕНИЯ СЕРВИСОВ                     ║
    ║                                                                              ║
    ║  Система для отслеживания подписок, платежей и уведомлений о сроках         ║
    ║  истечения различных сервисов и подписок                                    ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Запускаем демонстрацию
    demonstrate_basic_operations()
    
    # Демонстрация управления подписками
    demonstrate_subscription_management()
    
    # Спрашиваем, хочет ли пользователь запустить интерактивное меню
    print("\n" + "="*80)
    choice = input("\n💡 Запустить интерактивное меню? (y/n): ").strip().lower()
    if choice == 'y':
        interactive_menu()
