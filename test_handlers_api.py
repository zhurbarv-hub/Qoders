"""
Тест новых команд бота с Web API интеграцией
"""
import asyncio
import sys
from datetime import date

print("=" * 70)
print("ТЕСТ ОБНОВЛЁННЫХ HANDLERS С WEB API")
print("=" * 70)

async def test_handlers():
    # 1. Проверка импортов
    print("\n1️⃣ Проверка импортов обновлённых модулей...")
    try:
        from bot.handlers import deadlines, admin
        from bot.services import formatter
        print("   ✅ Все handlers импортированы успешно")
    except Exception as e:
        print(f"   ❌ ОШИБКА импорта: {e}")
        return False
    
    # 2. Проверка новых функций форматирования
    print("\n2️⃣ Проверка новых функций в formatter.py...")
    try:
        # Проверяем наличие новых функций
        assert hasattr(formatter, 'format_api_statistics'), "Отсутствует format_api_statistics"
        assert hasattr(formatter, 'format_health_status'), "Отсутствует format_health_status"
        
        # Тестируем format_api_statistics
        test_stats = {
            'total_clients_count': 10,
            'active_clients_count': 8,
            'total_deadlines_count': 25,
            'active_deadlines_count': 20,
            'status_green': 12,
            'status_yellow': 5,
            'status_red': 3,
            'status_expired': 0,
            'data_source': 'api',
            'api_response_time': 56
        }
        
        stats_text = formatter.format_api_statistics(test_stats)
        assert 'Web API' in stats_text, "Не указан источник Web API"
        assert '56ms' in stats_text, "Не указано время ответа"
        print("   ✅ format_api_statistics работает")
        print(f"\n{stats_text}\n")
        
        # Тестируем format_health_status
        health_data = {
            'api_url': 'http://localhost:8000',
            'api_available': True,
            'response_time': 78,
            'token_valid': True,
            'stats': {'active_clients_count': 8, 'active_deadlines_count': 20}
        }
        
        health_text = formatter.format_health_status(health_data)
        assert 'Онлайн' in health_text, "Статус не показывает онлайн"
        assert '78 мс' in health_text, "Не указано время ответа"
        print("   ✅ format_health_status работает")
        print(f"\n{health_text}\n")
        
    except AssertionError as e:
        print(f"   ❌ ОШИБКА проверки: {e}")
        return False
    except Exception as e:
        print(f"   ❌ ОШИБКА выполнения: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Проверка новой команды /next в deadlines.py
    print("\n3️⃣ Проверка наличия команды /next...")
    try:
        # Проверяем что роутер содержит обработчик cmd_next
        handlers_list = [handler.callback.__name__ for handler in deadlines.router.message.handlers]
        assert 'cmd_next' in handlers_list, "Обработчик cmd_next не зарегистрирован"
        print("   ✅ Команда /next зарегистрирована")
    except Exception as e:
        print(f"   ❌ ОШИБКА: {e}")
        return False
    
    # 4. Проверка новой команды /health в admin.py
    print("\n4️⃣ Проверка наличия команды /health...")
    try:
        handlers_list = [handler.callback.__name__ for handler in admin.router.message.handlers]
        assert 'cmd_health' in handlers_list, "Обработчик cmd_health не зарегистрирован"
        print("   ✅ Команда /health зарегистрирована")
    except Exception as e:
        print(f"   ❌ ОШИБКА: {e}")
        return False
    
    # 5. Проверка интеграции с checker service
    print("\n5️⃣ Проверка интеграции checker service с API...")
    try:
        from bot.services import checker
        
        # Проверяем что checker имеет глобальную переменную api_client
        assert hasattr(checker, '_api_client'), "Отсутствует _api_client в checker"
        assert hasattr(checker, 'set_api_client'), "Отсутствует функция set_api_client"
        
        print("   ✅ Checker service готов к работе с API")
        
        # Тестируем получение дедлайнов (если API доступен)
        try:
            from bot.services.token_manager import TokenManager
            from bot.services.api_client import WebAPIClient
            from backend.config import settings
            
            token_manager = TokenManager(
                api_base_url=settings.web_api_base_url,
                username=settings.bot_api_username,
                password=settings.bot_api_password
            )
            
            api_client = WebAPIClient(
                base_url=settings.web_api_base_url,
                token_manager=token_manager,
                timeout=settings.web_api_timeout
            )
            
            checker.set_api_client(api_client)
            
            # Пробуем получить дедлайны
            deadlines = await checker.get_expiring_deadlines(14)
            print(f"   ✅ Получено {len(deadlines)} дедлайнов через checker (API или fallback)")
            
            await api_client.close()
            
        except Exception as e:
            print(f"   ⚠️ API недоступен, но fallback должен работать: {e}")
    
    except Exception as e:
        print(f"   ❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def main():
    success = await test_handlers()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 70)
        print("\n📋 Следующие шаги:")
        print("1. Запустите Web API сервер (если ещё не запущен):")
        print("   cd D:\\QoProj\\KKT\\web")
        print("   uvicorn app.main:app --reload")
        print("\n2. Запустите Telegram бота:")
        print("   cd D:\\QoProj\\KKT")
        print("   python bot/main.py")
        print("\n3. Протестируйте новые команды в Telegram:")
        print("   /status - статистика через API")
        print("   /health - проверка здоровья API")
        print("   /next 14 - дедлайны на 14 дней")
        print("   /next 30 - дедлайны на месяц")
    else:
        print("❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("=" * 70)
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())