"""
Тестирование API дедлайнов - проверка возвращаемых данных
"""
import requests
import json

API_BASE_URL = 'http://localhost:8000/api'

# Логин для получения токена (используйте ваши данные администратора)
login_data = {
    "username": "admin",
    "password": "admin123"
}

print("=" * 60)
print("ТЕСТИРОВАНИЕ API ДЕДЛАЙНОВ")
print("=" * 60)

# Получаем токен
print("\n1. Получение токена авторизации...")
try:
    response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
    if response.ok:
        token_data = response.json()
        token = token_data['access_token']
        print(f"✅ Токен получен: {token[:20]}...")
    else:
        print(f"❌ Ошибка авторизации: {response.status_code}")
        print(response.text)
        exit(1)
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    exit(1)

# Получаем список дедлайнов
print("\n2. Получение списка дедлайнов...")
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

try:
    response = requests.get(f"{API_BASE_URL}/deadlines", headers=headers)
    if response.ok:
        data = response.json()
        print(f"✅ Получено дедлайнов: {data.get('total', 0)}")
        
        if data.get('deadlines'):
            print("\n" + "=" * 60)
            print("ДЕТАЛИ ДЕДЛАЙНОВ:")
            print("=" * 60)
            
            for idx, deadline in enumerate(data['deadlines'], 1):
                print(f"\n📋 Дедлайн #{idx} (ID: {deadline.get('id')})")
                print(f"   Дата истечения: {deadline.get('expiration_date')}")
                print(f"   Дней до истечения: {deadline.get('days_until_expiration')}")
                print(f"   Статус: {deadline.get('status')}")
                
                # Проверяем данные клиента
                client = deadline.get('client')
                if client:
                    print(f"   📍 Клиент:")
                    print(f"      - ID: {client.get('id')}")
                    print(f"      - Название: {client.get('company_name')}")
                    print(f"      - ИНН: {client.get('inn')}")
                else:
                    print(f"   ⚠️  Клиент: НЕ НАЙДЕН (null)")
                
                # Проверяем данные типа услуги
                deadline_type = deadline.get('deadline_type')
                if deadline_type:
                    print(f"   🔖 Тип услуги:")
                    print(f"      - ID: {deadline_type.get('id')}")
                    print(f"      - Название (name): {deadline_type.get('name')}")
                    print(f"      - Название (type_name): {deadline_type.get('type_name')}")
                else:
                    print(f"   ⚠️  Тип услуги: НЕ НАЙДЕН (null)")
                
                print(f"   Уведомления: {deadline.get('notification_enabled')}")
                
                # Полный JSON для первого дедлайна
                if idx == 1:
                    print("\n" + "-" * 60)
                    print("ПОЛНЫЙ JSON ПЕРВОГО ДЕДЛАЙНА:")
                    print("-" * 60)
                    print(json.dumps(deadline, indent=2, ensure_ascii=False))
        else:
            print("   Нет дедлайнов в системе")
    else:
        print(f"❌ Ошибка получения дедлайнов: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Ошибка запроса: {e}")

print("\n" + "=" * 60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 60)
