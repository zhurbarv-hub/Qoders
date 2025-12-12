"""
Быстрый тест API эндпоинтов
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ API ЭНДПОИНТОВ")
    print("=" * 60)
    
    # 1. Проверка здоровья сервера
    print("\n1️⃣  Проверка сервера...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"   ✓ Сервер работает: {response.json()}")
        else:
            print(f"   ✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Сервер недоступен: {e}")
        print("   ℹ  Запустите сервер командой: uvicorn backend.main:app --reload")
        return
    
    # 2. Авторизация администратора
    print("\n2️⃣  Авторизация...")
    try:
        auth_data = {
            "username": "admin@kkt.ru",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", data=auth_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"   ✓ Получен токен: {token[:30]}...")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   ✗ Ошибка авторизации: {response.json()}")
            return
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return
    
    # 3. Получение списка пользователей
    print("\n3️⃣  Получение списка пользователей...")
    try:
        response = requests.get(f"{BASE_URL}/api/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"   ✓ Найдено пользователей: {users.get('total', 0)}")
            for user in users.get('users', [])[:3]:
                print(f"      - {user['full_name']} ({user['role']})")
        else:
            print(f"   ✗ Ошибка: {response.json()}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 4. Фильтрация клиентов
    print("\n4️⃣  Получение только клиентов...")
    try:
        response = requests.get(f"{BASE_URL}/api/users?role=client", headers=headers)
        if response.status_code == 200:
            clients = response.json()
            print(f"   ✓ Найдено клиентов: {clients.get('total', 0)}")
            for client in clients.get('users', []):
                print(f"      - {client.get('company_name')} (ИНН: {client.get('inn')})")
        else:
            print(f"   ✗ Ошибка: {response.json()}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 5. Получение типов дедлайнов
    print("\n5️⃣  Получение типов дедлайнов...")
    try:
        response = requests.get(f"{BASE_URL}/api/deadline-types", headers=headers)
        if response.status_code == 200:
            types = response.json()
            print(f"   ✓ Найдено типов: {len(types)}")
            for dt in types:
                print(f"      - {dt['type_name']}")
        else:
            print(f"   ✗ Ошибка: {response.json()}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    # 6. Статистика дашборда
    print("\n6️⃣  Получение статистики дашборда...")
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/statistics", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✓ Статистика получена:")
            print(f"      - Всего клиентов: {stats.get('total_clients', 0)}")
            print(f"      - Активных клиентов: {stats.get('active_clients', 0)}")
            print(f"      - Всего дедлайнов: {stats.get('total_deadlines', 0)}")
        else:
            print(f"   ✗ Ошибка: {response.json()}")
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("✅ ТЕСТИРОВАНИЕ API ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
