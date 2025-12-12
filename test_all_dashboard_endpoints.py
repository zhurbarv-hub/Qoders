"""
Полный тест всех endpoints дашбоарда
"""
import requests
import json

API_BASE_URL = 'http://localhost:8000/api'

# Авторизация
login_data = {
    "username": "admin",
    "password": "admin123"
}

try:
    # Получаем токен
    response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
    response.raise_for_status()
    token = response.json()['access_token']
    print(f"✓ Авторизация успешна")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Тест 1: /api/dashboard/stats
    print("\n=== ТЕСТ 1: /api/dashboard/stats ===")
    response = requests.get(f"{API_BASE_URL}/dashboard/stats", headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        print(f"✓ Данные получены")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print(f"✗ Ошибка: {response.text}")
    
    # Тест 2: /api/deadlines/urgent
    print("\n=== ТЕСТ 2: /api/deadlines/urgent?days=14 ===")
    response = requests.get(f"{API_BASE_URL}/deadlines/urgent?days=14", headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"✓ Срочных дедлайнов: {len(data)}")
        if len(data) > 0:
            print(f"Пример: {data[0].get('client', {}).get('company_name', 'N/A')}")
    else:
        print(f"✗ Ошибка: {response.text}")
    
    # Тест 3: /api/deadline-types
    print("\n=== ТЕСТ 3: /api/deadline-types ===")
    response = requests.get(f"{API_BASE_URL}/deadline-types", headers=headers)
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"✓ Типов услуг: {len(data)}")
        if len(data) > 0:
            print(f"Пример: {data[0].get('type_name', 'N/A')}")
    else:
        print(f"✗ Ошибка: {response.text}")
        
    print("\n✓ Все тесты пройдены!")
    
except requests.exceptions.RequestException as e:
    print(f"✗ Ошибка запроса: {e}")
except Exception as e:
    print(f"✗ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc()
