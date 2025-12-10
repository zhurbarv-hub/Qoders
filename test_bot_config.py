"""
Тестовый скрипт для проверки конфигурации Telegram бота
"""

def test_configuration():
    """Проверка всех параметров конфигурации"""
    
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ КОНФИГУРАЦИИ TELEGRAM БОТА")
    print("=" * 60)
    
    # Тест 1: Импорт модуля
    print("\n[1/5] Проверка импорта модуля конфигурации...")
    try:
        from bot.config import get_bot_config, validate_bot_token
        print("    ✅ Модуль импортирован успешно")
    except ImportError as e:
        print(f"    ❌ Ошибка импорта: {e}")
        return False
    
    # Тест 2: Загрузка конфигурации
    print("\n[2/5] Загрузка конфигурации...")
    try:
        config = get_bot_config()
        print("    ✅ Конфигурация загружена")
    except ValueError as e:
        print(f"    ❌ Ошибка валидации: {e}")
        return False
    except Exception as e:
        print(f"    ❌ Неожиданная ошибка: {e}")
        return False
    
    # Тест 3: Проверка токена бота
    print("\n[3/5] Валидация токена бота...")
    if validate_bot_token(config.telegram_bot_token):
        print(f"    ✅ Токен валиден")
        print(f"    📱 Первые 20 символов: {config.telegram_bot_token[:20]}...")
    else:
        print(f"    ❌ Токен невалиден")
        return False
    
    # Тест 4: Проверка Admin ID
    print("\n[4/5] Проверка Admin ID...")
    if config.telegram_admin_id > 0:
        print(f"    ✅ Admin ID: {config.telegram_admin_id}")
    else:
        print(f"    ❌ Некорректный Admin ID: {config.telegram_admin_id}")
        return False
    
    # Тест 5: Проверка настроек уведомлений
    print("\n[5/5] Проверка настроек уведомлений...")
    try:
        days_list = config.notification_days_list
        print(f"    ✅ Дни уведомлений: {days_list}")
        print(f"    ⏰ Время проверки: {config.notification_check_time}")
        print(f"    🌍 Часовой пояс: {config.notification_timezone}")
        print(f"    🔄 Попыток повтора: {config.notification_retry_attempts}")
        print(f"    ⏱️ Задержка повтора: {config.notification_retry_delay} сек")
    except Exception as e:
        print(f"    ❌ Ошибка параметров уведомлений: {e}")
        return False
    
    # Итоги
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)
    print("\n📋 Сводка конфигурации:")
    print(f"   Токен бота: {config.telegram_bot_token[:15]}...")
    print(f"   Admin ID: {config.telegram_admin_id}")
    print(f"   Уведомления за: {days_list} дней")
    print(f"   Проверка в: {config.notification_check_time} ({config.notification_timezone})")
    print(f"   База данных: {config.database_path}")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_configuration()
        if not success:
            print("\n⚠️ ТЕСТИРОВАНИЕ НЕ ПРОЙДЕНО!")
            print("Проверьте файл .env и убедитесь, что все параметры заполнены корректно.")
            exit(1)
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        exit(1)