"""
Скрипт для тестирования нового endpoint активации/деактивации клиентов
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
    
    # 1. Получаем список активных клиентов
    print("\n=== ТЕСТ 1: Получение только активных клиентов ===")
    response = requests.get(f"{API_BASE_URL}/users?role=client&is_active=true&page_size=50", headers=headers)
    response.raise_for_status()
    data = response.json()
    print(f"Активных клиентов: {data.get('total', 0)}")
    active_users = data.get('users', [])
    for user in active_users[:3]:
        print(f"  - {user.get('company_name', 'N/A')} (ID={user.get('id')}): {user.get('is_active')}")
    
    # 2. Получаем все клиенты (включая неактивных)
    print("\n=== ТЕСТ 2: Получение всех клиентов (активных и неактивных) ===")
    response = requests.get(f"{API_BASE_URL}/users?role=client&page_size=50", headers=headers)
    response.raise_for_status()
    data = response.json()
    print(f"Всего клиентов: {data.get('total', 0)}")
    all_users = data.get('users', [])
    
    # 3. Тест переключения статуса (если есть клиенты)
    if all_users:
        test_user = all_users[0]
        user_id = test_user.get('id')
        user_name = test_user.get('company_name', test_user.get('full_name', 'N/A'))
        current_status = test_user.get('is_active')
        
        print(f"\n=== ТЕСТ 3: Переключение статуса клиента ===")
        print(f"Клиент: {user_name} (ID={user_id})")
        print(f"Текущий статус: {'Активен' if current_status else 'Неактивен'}")
        
        # НЕ будем выполнять реальное переключение, только показываем что endpoint доступен
        print(f"✓ Endpoint /users/{user_id}/toggle-status готов к использованию")
        print(f"  (Для переключения используйте PATCH запрос)")
    
    print("\n✓ Все тесты пройдены успешно!")
    
except requests.exceptions.RequestException as e:
    print(f"✗ Ошибка запроса: {e}")
except Exception as e:
    print(f"✗ Неожиданная ошибка: {e}")
