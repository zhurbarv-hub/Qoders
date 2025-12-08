"""
Тестовый скрипт для проверки работы СУБД
Можно запустить при наличии Python
"""

import sys
import os

def test_database():
    """Тестирование базы данных"""
    print("🧪 Тестирование СУБД для фиксации сроков истечения сервисов\n")
    
    try:
        from service_tracker import ServiceTracker
        from datetime import datetime, timedelta
        
        print("✅ Модули успешно импортированы")
        
        # Создаем временную базу данных для теста
        test_db = "test_services.db"
        
        print(f"\n📁 Создание тестовой базы данных: {test_db}")
        
        with ServiceTracker(test_db) as tracker:
            print("✅ База данных инициализирована")
            
            # Тест 1: Добавление сервиса
            print("\n🔸 Тест 1: Добавление сервиса")
            service_id = tracker.add_service(
                service_name="Тестовый сервис",
                description="Описание тестового сервиса",
                provider="Тестовый провайдер",
                category="Тест",
                cost=100.00,
                currency="RUB"
            )
            print(f"✅ Сервис добавлен с ID: {service_id}")
            
            # Тест 2: Получение сервиса
            print("\n🔸 Тест 2: Получение сервиса")
            service = tracker.get_service(service_id)
            print(f"✅ Получен сервис: {service['service_name']}")
            
            # Тест 3: Добавление подписки
            print("\n🔸 Тест 3: Добавление подписки")
            today = datetime.now().date()
            sub_id = tracker.add_subscription(
                service_id=service_id,
                start_date=today.strftime('%Y-%m-%d'),
                expiration_date=(today + timedelta(days=30)).strftime('%Y-%m-%d'),
                subscription_type="monthly",
                auto_renewal=True,
                notification_days=7
            )
            print(f"✅ Подписка добавлена с ID: {sub_id}")
            
            # Тест 4: Получение активных подписок
            print("\n🔸 Тест 4: Получение активных подписок")
            active_subs = tracker.get_active_subscriptions()
            print(f"✅ Найдено активных подписок: {len(active_subs)}")
            
            # Тест 5: Добавление платежа
            print("\n🔸 Тест 5: Добавление платежа")
            payment_id = tracker.add_payment(
                subscription_id=sub_id,
                payment_date=today.strftime('%Y-%m-%d'),
                amount=100.00,
                currency="RUB",
                payment_method="Тестовая карта"
            )
            print(f"✅ Платеж добавлен с ID: {payment_id}")
            
            # Тест 6: Генерация уведомлений
            print("\n🔸 Тест 6: Генерация уведомлений")
            notif_count = tracker.generate_notifications_for_expiring_subscriptions()
            print(f"✅ Создано уведомлений: {notif_count}")
            
            # Тест 7: Статистика
            print("\n🔸 Тест 7: Получение статистики")
            stats = tracker.get_statistics()
            print(f"✅ Активных сервисов: {stats['active_services']}")
            print(f"✅ Активных подписок: {stats['active_subscriptions']}")
            print(f"✅ Сумма платежей: {stats['total_payments']:.2f}")
            
            # Тест 8: Экспорт
            print("\n🔸 Тест 8: Экспорт данных")
            tracker.export_to_json("test_export.json")
            print(f"✅ Данные экспортированы")
        
        print("\n" + "="*70)
        print("✨ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ✨")
        print("="*70)
        
        # Очистка тестовых файлов
        if os.path.exists(test_db):
            os.remove(test_db)
            print(f"\n🧹 Тестовая база данных удалена")
        
        if os.path.exists("test_export.json"):
            os.remove("test_export.json")
            print(f"🧹 Тестовый экспорт удален")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("\n💡 Убедитесь, что файлы service_tracker.py и schema.sql находятся в той же директории")
        return False
    
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      ТЕСТИРОВАНИЕ СУБД                                        ║
║          Система отслеживания сроков истечения сервисов                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    success = test_database()
    sys.exit(0 if success else 1)
