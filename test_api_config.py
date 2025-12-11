# -*- coding: utf-8 -*-
"""
Тестирование конфигурации Web API Integration
"""

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Тестирование загрузки конфигурации"""
    print("=" * 70)
    print("ТЕСТ КОНФИГУРАЦИИ WEB API INTEGRATION")
    print("=" * 70)
    
    try:
        from backend.config import settings
        
        print("\n✅ Конфигурация успешно загружена!")
        print("\n" + "=" * 70)
        print("ПРОВЕРКА НОВЫХ ПОЛЕЙ:")
        print("=" * 70)
        
        # Проверка Web API полей
        print(f"\n🔌 Web API Integration:")
        print(f"   ├─ Base URL: {settings.web_api_base_url}")
        print(f"   ├─ Timeout: {settings.web_api_timeout} секунд")
        print(f"   ├─ Bot Username: {settings.bot_api_username}")
        print(f"   ├─ Bot Password: {'*' * len(settings.bot_api_password)}")
        print(f"   └─ Token Refresh: {settings.bot_token_refresh_interval} секунд ({settings.bot_token_refresh_interval // 60} минут)")
        
        # Проверка типов данных
        print(f"\n🔍 Проверка типов данных:")
        assert isinstance(settings.web_api_base_url, str), "web_api_base_url должен быть строкой"
        print(f"   ✓ web_api_base_url: str")
        
        assert isinstance(settings.web_api_timeout, int), "web_api_timeout должен быть числом"
        print(f"   ✓ web_api_timeout: int")
        
        assert isinstance(settings.bot_api_username, str), "bot_api_username должен быть строкой"
        print(f"   ✓ bot_api_username: str")
        
        assert isinstance(settings.bot_api_password, str), "bot_api_password должен быть строкой"
        print(f"   ✓ bot_api_password: str")
        
        assert isinstance(settings.bot_token_refresh_interval, int), "bot_token_refresh_interval должен быть числом"
        print(f"   ✓ bot_token_refresh_interval: int")
        
        # Проверка значений
        print(f"\n🎯 Проверка значений:")
        assert settings.web_api_timeout > 0, "Timeout должен быть положительным"
        print(f"   ✓ Timeout > 0")
        
        assert settings.bot_token_refresh_interval > 0, "Refresh interval должен быть положительным"
        print(f"   ✓ Refresh interval > 0")
        
        assert settings.web_api_base_url.startswith("http"), "URL должен начинаться с http"
        print(f"   ✓ URL начинается с http")
        
        assert len(settings.bot_api_username) > 0, "Username не должен быть пустым"
        print(f"   ✓ Username не пустой")
        
        assert len(settings.bot_api_password) > 0, "Password не должен быть пустым"
        print(f"   ✓ Password не пустой")
        
        print("\n" + "=" * 70)
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)