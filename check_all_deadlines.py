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
    
    # Получаем дедлайны
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(f"{API_BASE_URL}/deadlines?page=1&page_size=50", headers=headers)
    response.raise_for_status()
    data = response.json()
    
    print(f"\n=== РЕЗУЛЬТАТЫ API ===")
    print(f"Всего дедлайнов (total): {data.get('total', 0)}")
    print(f"Получено дедлайнов (deadlines.length): {len(data.get('deadlines', []))}")
    
    if data.get('total') != len(data.get('deadlines', [])):
        print(f"\n⚠ ВНИМАНИЕ: Несоответствие! API сообщает {data['total']} дедлайнов, но вернул {len(data['deadlines'])}")
    
    print(f"\n=== СПИСОК ВСЕХ ДЕДЛАЙНОВ ===")
    for idx, deadline in enumerate(data.get('deadlines', []), 1):
        client_name = "НЕТ КЛИЕНТА"
        if deadline.get('client'):
            client_name = deadline['client'].get('company_name') or deadline['client'].get('name') or "НЕТ КЛИЕНТА"
        
        type_name = "НЕТ ТИПА"
        if deadline.get('deadline_type'):
            type_name = deadline['deadline_type'].get('name') or deadline['deadline_type'].get('type_name') or "НЕТ ТИПА"
        
        days = deadline.get('days_until_expiration', '?')
        exp_date = deadline.get('expiration_date', '?')
        
        print(f"{idx}. ID={deadline.get('id')}, Клиент=\"{client_name}\", Тип=\"{type_name}\", Дней={days}, Дата={exp_date}")
    
    # Проверяем пагинацию
    if data.get('total', 0) > 50:
        print(f"\n⚠ ВНИМАНИЕ: Всего {data['total']} дедлайнов, возможно нужна пагинация!")
        
except requests.exceptions.RequestException as e:
    print(f"✗ Ошибка запроса: {e}")
except Exception as e:
    print(f"✗ Неожиданная ошибка: {e}")
