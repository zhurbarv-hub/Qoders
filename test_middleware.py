"""
Тестирование middleware
"""

def test_middleware():
    """Тест middleware компонентов"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ MIDDLEWARE")
    print("=" * 60)
    
    # Тест 1: Импорт
    print("\n[1/2] Проверка импорта middleware...")
    try:
        from bot.middlewares import AuthMiddleware, LoggingMiddleware
        from bot.middlewares.auth import is_admin, get_client_by_telegram_id
        print("    ✅ Все middleware импортированы успешно")
    except ImportError as e:
        print(f"    ❌ Ошибка импорта: {e}")
        return False
    
    # Тест 2: Проверка функции is_admin
    print("\n[2/2] Проверка функции is_admin...")
    try:
        from backend.config import settings
        
        # Проверяем что admin ID распознаётся
        result = is_admin(settings.telegram_admin_id)
        assert result == True, "Admin ID не распознан"
        
        # Проверяем что случайный ID не admin
        result = is_admin(999999999)
        assert result == False, "Случайный ID распознан как admin"
        
        print("    ✅ Функция is_admin работает корректно")
        print(f"       Admin ID: {settings.telegram_admin_id}")
        
    except Exception as e:
        print(f"    ❌ Ошибка: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ MIDDLEWARE ПРОЙДЕНЫ!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_middleware()
        if not success:
            exit(1)
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        exit(1)