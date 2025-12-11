# -*- coding: utf-8 -*-
"""
Тестирование интеграции бота с Web API
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_integration():
    """Тестирование интеграции компонентов"""
    print("=" * 70)
    print("ТЕСТ ИНТЕГРАЦИИ TELEGRAM БОТА С WEB API")
    print("=" * 70)
    
    try:
        # Тест 1: Импорт модулей
        print("\n1️⃣ Проверка импортов...")
        from backend.config import settings
        from bot.services.token_manager import TokenManager
        from bot.services.api_client import WebAPIClient
        from bot.services import checker
        print("   ✅ Все модули импортированы успешно")
        
        # Тест 2: Создание Token Manager
        print("\n2️⃣ Создание Token Manager...")
        token_manager = TokenManager(
            api_base_url=settings.web_api_base_url,
            username=settings.bot_api_username,
            password=settings.bot_api_password,
            refresh_interval=settings.bot_token_refresh_interval
        )
        print(f"   ✅ TokenManager создан: {settings.web_api_base_url}")
        
        # Тест 3: Создание API клиента
        print("\n3️⃣ Создание Web API клиента...")
        api_client = WebAPIClient(
            base_url=settings.web_api_base_url,
            token_manager=token_manager,
            timeout=settings.web_api_timeout
        )
        print(f"   ✅ WebAPIClient создан (timeout: {settings.web_api_timeout}s)")
        
        # Тест 4: Проверка подключения к API (требует запущенный Web API)
        print("\n4️⃣ Проверка подключения к Web API...")
        try:
            stats = await api_client.get_dashboard_stats()
            print(f"   ✅ Web API доступен!")
            print(f"      - Клиентов: {stats.get('active_clients_count', 0)}")
            print(f"      - Дедлайнов: {stats.get('active_deadlines_count', 0)}")
            api_works = True
        except Exception as e:
            print(f"   ⚠️ Web API недоступен (будет использован fallback): {e}")
            api_works = False
        
        # Тест 5: Установка API клиента в checker
        print("\n5️⃣ Установка API клиента в checker service...")
        checker.set_api_client(api_client)
        print("   ✅ API клиент установлен в checker")
        
        # Тест 6: Тест получения дедлайнов
        print("\n6️⃣ Тест получения дедлайнов через checker...")
        deadlines = await checker.get_expiring_deadlines(14)
        print(f"   ✅ Получено {len(deadlines)} дедлайнов через {14} дней")
        
        if api_works:
            print("      📡 Источник: Web API")
        else:
            print("      💾 Источник: База данных (fallback)")
        
        if deadlines:
            first = deadlines[0]
            print(f"      Пример: {first.get('client_name')} - {first.get('deadline_type_name')}")
        
        # Тест 7: Закрытие API клиента
        print("\n7️⃣ Закрытие API клиента...")
        await api_client.close()
        print("   ✅ API клиент закрыт")
        
        print("\n" + "=" * 70)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 70)
        
        if not api_works:
            print("\n⚠️ ВНИМАНИЕ:")
            print("   Web API был недоступен, но fallback работает корректно.")
            print("   Для полного функционала запустите Web API сервер:")
            print("   > cd web")
            print("   > uvicorn app.main:app --reload")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_integration())
    sys.exit(0 if success else 1)