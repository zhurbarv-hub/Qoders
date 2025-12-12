import requests

API_BASE_URL = 'http://localhost:8000/api'

# Авторизация
login_data = {"username": "admin", "password": "admin123"}

response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
token = response.json()['access_token']

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Проверяем дедлайн ID=11 напрямую
print("Запрашиваем дедлайн ID=11...")
response = requests.get(f"{API_BASE_URL}/deadlines/11", headers=headers)

print(f"Статус: {response.status_code}")
print(f"Ответ: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"\nУспешно получен дедлайн:")
    print(f"  ID: {data.get('id')}")
    print(f"  Client: {data.get('client')}")
    print(f"  Type: {data.get('deadline_type')}")
elif response.status_code == 404:
    print("\nДедлайн не найден!")
else:
    print(f"\nОшибка: {response.status_code}")
