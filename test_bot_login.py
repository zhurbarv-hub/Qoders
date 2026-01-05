# -*- coding: utf-8 -*-
"""
Тест авторизации бота в Web API
Проверка учётных данных из .env файла
"""
import requests
import json
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

def test_bot_login():
    """Тестирование логина бота"""
    
    # Параметры из .env
    api_url = os.getenv('WEB_API_BASE_URL', 'http://localhost:8000')
    username = os.getenv('BOT_API_USERNAME', 'admin')
    password = os.getenv('BOT_API_PASSWORD', 'admin')
    
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ АВТОРИЗАЦИИ БОТА В WEB API")
    print("=" * 70)
    print(f"\n📋 Параметры:")
    print(f"   API URL: {api_url}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)} ({len(password)} символов)")
    
    # Проверка длины пароля
    if len(password) < 6:
        print(f"\n❌ ОШИБКА: Пароль слишком короткий ({len(password)} символов)")
        print("   Web API требует минимум 6 символов")
        print("   Обновите BOT_API_PASSWORD в .env файле")
        return False
    
    # Попытка логина
    login_url = f"{api_url}/api/auth/login"
    
    print(f"\n🔗 Запрос к: {login_url}")
    print(f"   Метод: POST")
    print(f"   Данные: {{'username': '{username}', 'password': '***'}}")
    
    try:
        response = requests.post(
            login_url,
            json={
                'username': username,
                'password': password
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📡 Ответ сервера:")
        print(f"   HTTP статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ УСПЕШНО!")
            print(f"\n🎟️  Токен получен:")
            print(f"   Access Token: {data.get('access_token', '')[:50]}...")
            print(f"   Token Type: {data.get('token_type', 'N/A')}")
            
            if 'user' in data:
                user = data['user']
                print(f"\n👤 Информация о пользователе:")
                print(f"   ID: {user.get('id')}")
                print(f"   Username: {user.get('username')}")
                print(f"   Email: {user.get('email')}")
                print(f"   Role: {user.get('role')}")
                print(f"   Full Name: {user.get('full_name')}")
            
            print("\n" + "=" * 70)
            print("✅ АВТОРИЗАЦИЯ УСПЕШНА!")
            print("=" * 70)
            print("\n📋 Следующие шаги:")
            print("   1. Перезапустите Telegram бота")
            print("   2. Бот должен автоматически получить токен")
            print("   3. Проверьте логи бота на наличие сообщения '✅ Токен успешно обновлён'")
            print()
            return True
            
        elif response.status_code == 422:
            error_data = response.json()
            print(f"   ❌ ОШИБКА ВАЛИДАЦИИ (HTTP 422)")
            print(f"\n   Детали:")
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
            
            if 'detail' in error_data and isinstance(error_data['detail'], list):
                for err in error_data['detail']:
                    if 'loc' in err and 'password' in err['loc']:
                        print(f"\n   ⚠️  Проблема с паролем:")
                        print(f"      Тип: {err.get('type', 'unknown')}")
                        print(f"      Сообщение: {err.get('msg', 'N/A')}")
            
            print("\n💡 Рекомендации:")
            print("   - Убедитесь, что пароль содержит минимум 6 символов")
            print("   - Проверьте BOT_API_PASSWORD в .env файле")
            return False
            
        elif response.status_code == 401:
            print(f"   ❌ НЕВЕРНЫЕ УЧЁТНЫЕ ДАННЫЕ (HTTP 401)")
            error_data = response.json()
            print(f"   Сообщение: {error_data.get('detail', 'N/A')}")
            
            print("\n💡 Рекомендации:")
            print("   - Проверьте правильность username и password в .env")
            print("   - Убедитесь, что пользователь существует в БД")
            print("   - Запустите fix_bot_password_direct.py для установки пароля")
            return False
            
        else:
            print(f"   ❌ НЕОЖИДАННЫЙ ОТВЕТ (HTTP {response.status_code})")
            try:
                error_data = response.json()
                print(f"   Данные: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Текст: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ")
        print(f"   Не удалось подключиться к {api_url}")
        print("\n💡 Рекомендации:")
        print("   - Убедитесь, что Web API запущен")
        print("   - Проверьте правильность WEB_API_BASE_URL в .env")
        print("   - Запустите Web API командой: python -m uvicorn web.app.main:app --reload")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n❌ ТАЙМАУТ")
        print(f"   Сервер не ответил в течение 10 секунд")
        return False
        
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_bot_login()
    sys.exit(0 if success else 1)
# -*- coding: utf-8 -*-
"""
Тест авторизации бота в Web API
Проверка учётных данных из .env файла
"""
import requests
import json
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

def test_bot_login():
    """Тестирование логина бота"""
    
    # Параметры из .env
    api_url = os.getenv('WEB_API_BASE_URL', 'http://localhost:8000')
    username = os.getenv('BOT_API_USERNAME', 'admin')
    password = os.getenv('BOT_API_PASSWORD', 'admin')
    
    print("=" * 70)
    print("🧪 ТЕСТИРОВАНИЕ АВТОРИЗАЦИИ БОТА В WEB API")
    print("=" * 70)
    print(f"\n📋 Параметры:")
    print(f"   API URL: {api_url}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)} ({len(password)} символов)")
    
    # Проверка длины пароля
    if len(password) < 6:
        print(f"\n❌ ОШИБКА: Пароль слишком короткий ({len(password)} символов)")
        print("   Web API требует минимум 6 символов")
        print("   Обновите BOT_API_PASSWORD в .env файле")
        return False
    
    # Попытка логина
    login_url = f"{api_url}/api/auth/login"
    
    print(f"\n🔗 Запрос к: {login_url}")
    print(f"   Метод: POST")
    print(f"   Данные: {{'username': '{username}', 'password': '***'}}")
    
    try:
        response = requests.post(
            login_url,
            json={
                'username': username,
                'password': password
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📡 Ответ сервера:")
        print(f"   HTTP статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ УСПЕШНО!")
            print(f"\n🎟️  Токен получен:")
            print(f"   Access Token: {data.get('access_token', '')[:50]}...")
            print(f"   Token Type: {data.get('token_type', 'N/A')}")
            
            if 'user' in data:
                user = data['user']
                print(f"\n👤 Информация о пользователе:")
                print(f"   ID: {user.get('id')}")
                print(f"   Username: {user.get('username')}")
                print(f"   Email: {user.get('email')}")
                print(f"   Role: {user.get('role')}")
                print(f"   Full Name: {user.get('full_name')}")
            
            print("\n" + "=" * 70)
            print("✅ АВТОРИЗАЦИЯ УСПЕШНА!")
            print("=" * 70)
            print("\n📋 Следующие шаги:")
            print("   1. Перезапустите Telegram бота")
            print("   2. Бот должен автоматически получить токен")
            print("   3. Проверьте логи бота на наличие сообщения '✅ Токен успешно обновлён'")
            print()
            return True
            
        elif response.status_code == 422:
            error_data = response.json()
            print(f"   ❌ ОШИБКА ВАЛИДАЦИИ (HTTP 422)")
            print(f"\n   Детали:")
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
            
            if 'detail' in error_data and isinstance(error_data['detail'], list):
                for err in error_data['detail']:
                    if 'loc' in err and 'password' in err['loc']:
                        print(f"\n   ⚠️  Проблема с паролем:")
                        print(f"      Тип: {err.get('type', 'unknown')}")
                        print(f"      Сообщение: {err.get('msg', 'N/A')}")
            
            print("\n💡 Рекомендации:")
            print("   - Убедитесь, что пароль содержит минимум 6 символов")
            print("   - Проверьте BOT_API_PASSWORD в .env файле")
            return False
            
        elif response.status_code == 401:
            print(f"   ❌ НЕВЕРНЫЕ УЧЁТНЫЕ ДАННЫЕ (HTTP 401)")
            error_data = response.json()
            print(f"   Сообщение: {error_data.get('detail', 'N/A')}")
            
            print("\n💡 Рекомендации:")
            print("   - Проверьте правильность username и password в .env")
            print("   - Убедитесь, что пользователь существует в БД")
            print("   - Запустите fix_bot_password_direct.py для установки пароля")
            return False
            
        else:
            print(f"   ❌ НЕОЖИДАННЫЙ ОТВЕТ (HTTP {response.status_code})")
            try:
                error_data = response.json()
                print(f"   Данные: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"   Текст: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ")
        print(f"   Не удалось подключиться к {api_url}")
        print("\n💡 Рекомендации:")
        print("   - Убедитесь, что Web API запущен")
        print("   - Проверьте правильность WEB_API_BASE_URL в .env")
        print("   - Запустите Web API командой: python -m uvicorn web.app.main:app --reload")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n❌ ТАЙМАУТ")
        print(f"   Сервер не ответил в течение 10 секунд")
        return False
        
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_bot_login()
    sys.exit(0 if success else 1)
