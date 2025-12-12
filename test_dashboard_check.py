import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_dashboard():
    print("=" * 50)
    print("ТЕСТ ДАШБОРДА")
    print("=" * 50)
    
    # Логин
    print("\n1. Попытка авторизации...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            },
            timeout=5
        )
        print(f"   Статус логина: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   Ошибка логина: {login_response.text}")
            return
            
        login_data = login_response.json()
        print(f"   Ключи ответа: {login_data.keys()}")
        
        if 'access_token' not in login_data:
            print(f"   ОШИБКА: access_token отсутствует!")
            print(f"   Полный ответ: {json.dumps(login_data, indent=2, ensure_ascii=False)}")
            return
            
        token = login_data['access_token']
        print(f"   ✅ Токен получен: {token[:20]}...")
        
    except Exception as e:
        print(f"   ❌ Ошибка при логине: {e}")
        return
    
    # Проверка эндпоинта dashboard/stats
    print("\n2. Запрос dashboard/stats...")
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        stats_response = requests.get(
            f"{BASE_URL}/dashboard/stats",
            headers=headers,
            timeout=5
        )
        
        print(f"   Статус: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"   ✅ Данные получены:")
            print(f"      - Всего клиентов: {stats_data.get('total_clients', 0)}")
            print(f"      - Активных: {stats_data.get('active_clients', 0)}")
            print(f"      - Всего дедлайнов: {stats_data.get('total_deadlines', 0)}")
            print(f"      - Зеленых: {stats_data.get('status_green', 0)}")
            print(f"      - Желтых: {stats_data.get('status_yellow', 0)}")
            print(f"      - Красных: {stats_data.get('status_red', 0)}")
            print(f"      - Просроченных: {stats_data.get('status_expired', 0)}")
        else:
            print(f"   ❌ Ошибка: {stats_response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка при запросе: {e}")
    
    # Проверка эндпоинта deadlines/urgent
    print("\n3. Запрос deadlines/urgent...")
    try:
        urgent_response = requests.get(
            f"{BASE_URL}/deadlines/urgent?days=14",
            headers=headers,
            timeout=5
        )
        
        print(f"   Статус: {urgent_response.status_code}")
        
        if urgent_response.status_code == 200:
            urgent_data = urgent_response.json()
            print(f"   ✅ Срочных дедлайнов: {len(urgent_data)}")
        else:
            print(f"   ❌ Ошибка: {urgent_response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка при запросе: {e}")
    
    # Проверка эндпоинта deadline-types
    print("\n4. Запрос deadline-types...")
    try:
        types_response = requests.get(
            f"{BASE_URL}/deadline-types",
            headers=headers,
            timeout=5
        )
        
        print(f"   Статус: {types_response.status_code}")
        
        if types_response.status_code == 200:
            types_data = types_response.json()
            print(f"   ✅ Типов услуг: {len(types_data)}")
        else:
            print(f"   ❌ Ошибка: {types_response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка при запросе: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_dashboard()
