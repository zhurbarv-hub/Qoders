"""
Тестовый скрипт для проверки API пользователей
"""
import requests
import json

API_URL = "http://localhost:8000/api"

# Сначала авторизуемся
print("=" * 60)
print("ТЕСТ API ПОЛЬЗОВАТЕЛЕЙ")
print("=" * 60)

# Авторизация
print("\n1. Авторизация...")
auth_response = requests.post(
    f"{API_URL}/auth/login",
    json={"username": "admin", "password": "admin123"}
)

if auth_response.status_code == 200:
    auth_data = auth_response.json()
    token = auth_data["access_token"]
    print(f"✅ Авторизация успешна! Token: {token[:20]}...")
else:
    print(f"❌ Ошибка авторизации: {auth_response.status_code}")
    print(auth_response.text)
    exit(1)

# Проверка списка пользователей (все)
print("\n2. Получение всех пользователей...")
users_response = requests.get(
    f"{API_URL}/users?page=1&page_size=100",
    headers={"Authorization": f"Bearer {token}"}
)

if users_response.status_code == 200:
    users_data = users_response.json()
    print(f"✅ Получено пользователей: {users_data['total']}")
    print(f"   Страниц: {users_data['total_pages']}")
else:
    print(f"❌ Ошибка: {users_response.status_code}")
    print(users_response.text)

# Проверка списка клиентов
print("\n3. Получение клиентов (role=client)...")
clients_response = requests.get(
    f"{API_URL}/users?role=client&page=1&page_size=100",
    headers={"Authorization": f"Bearer {token}"}
)

if clients_response.status_code == 200:
    clients_data = clients_response.json()
    print(f"✅ Получено клиентов: {clients_data['total']}")
    
    if clients_data['total'] > 0:
        print("\n   Список клиентов:")
        for user in clients_data['users'][:5]:  # Показываем первые 5
            print(f"   - ID: {user['id']}, {user.get('company_name', user['full_name'])}")
    else:
        print("   ⚠️  Клиентов не найдено!")
else:
    print(f"❌ Ошибка: {clients_response.status_code}")
    print(clients_response.text)

# Проверка deadline-types
print("\n4. Получение типов дедлайнов...")
types_response = requests.get(
    f"{API_URL}/deadline-types",
    headers={"Authorization": f"Bearer {token}"}
)

if types_response.status_code == 200:
    types_data = types_response.json()
    print(f"✅ Получено типов: {len(types_data)}")
    
    if len(types_data) > 0:
        print("\n   Список типов:")
        for dt in types_data[:5]:
            print(f"   - ID: {dt['id']}, {dt.get('type_name', dt.get('name', 'N/A'))}")
    else:
        print("   ⚠️  Типов дедлайнов не найдено!")
else:
    print(f"❌ Ошибка: {types_response.status_code}")
    print(types_response.text)

print("\n" + "=" * 60)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 60)
