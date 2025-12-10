"""
Тестирование сервисов бота
"""
from datetime import date, timedelta

def test_services():
    """Быстрый тест сервисов"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СЕРВИСОВ БОТА")
    print("=" * 60)
    
    # Тест 1: Импорт модулей
    print("\n[1/3] Проверка импорта модулей...")
    try:
        from bot.services import checker, formatter, notifier
        print("    ✅ Все модули импортированы успешно")
    except ImportError as e:
        print(f"    ❌ Ошибка импорта: {e}")
        return False
    
    # Тест 2: Проверка функций checker
    print("\n[2/3] Проверка функций checker...")
    try:
        funcs = ['get_expiring_deadlines', 'get_notification_recipients', 
                 'check_notification_sent', 'get_client_deadlines']
        for func_name in funcs:
            assert hasattr(checker, func_name), f"Отсутствует {func_name}"
        print("    ✅ Все функции checker присутствуют")
    except AssertionError as e:
        print(f"    ❌ {e}")
        return False
    
    # Тест 3: Проверка функций formatter
    print("\n[3/3] Проверка форматирования...")
    try:
        # Тестовые данные
        test_deadline = {
            'client_name': 'Тестовая Компания',
            'client_inn': '1234567890',
            'deadline_type_name': 'ОФД',
            'expiration_date': date.today() + timedelta(days=7),
            'days_remaining': 7
        }
        
        message = formatter.format_deadline_notification(test_deadline, 7)
        
        # Проверяем что сообщение содержит ключевые элементы
        assert 'Тестовая Компания' in message
        assert '1234567890' in message
        assert 'ОФД' in message
        
        print("    ✅ Форматирование работает корректно")
        print(f"\n📝 Пример сообщения:\n{'-'*60}\n{message}\n{'-'*60}")
        
    except Exception as e:
        print(f"    ❌ Ошибка форматирования: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_services()
        if not success:
            print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
            exit(1)
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        exit(1)