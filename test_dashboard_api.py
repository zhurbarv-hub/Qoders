"""
Тест API дашбоарда
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
    
    # Тест dashboard stats
    print("\n=== ТЕСТ: /api/dashboard/stats ===")
    response = requests.get(f"{API_BASE_URL}/dashboard/stats", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print(f"✓ Данные получены:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"✗ Ошибка: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"✗ Ошибка запроса: {e}")
except Exception as e:
    print(f"✗ Неожиданная ошибка: {e}")
    import traceback
    traceback.print_exc()
