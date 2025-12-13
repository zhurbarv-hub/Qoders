# -*- coding: utf-8 -*-
"""
Тестирование API типов услуг - проверка прав доступа
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_deadline_types_access():
    """Тестирование доступа к управлению типами услуг"""
    
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ПРАВ ДОСТУПА К ТИПАМ УСЛУГ")
    print("="*60 + "\n")
    
    # Запросить логин и пароль
    username = input("Введите логин (admin или manager): ")
    password = input("Введите пароль: ")
    
    # 1. Авторизация
    print(f"\n1️⃣ Авторизация пользователя: {username}")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Ошибка авторизации: {login_response.status_code}")
        print(f"   {login_response.text}")
        return
    
    token_data = login_response.json()
    token = token_data.get("access_token")
    user_role = token_data.get("role")
    
    print(f"✅ Авторизация успешна")
    print(f"   Роль: {user_role}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Получить список типов
    print(f"\n2️⃣ Получение списка типов услуг")
    types_response = requests.get(f"{BASE_URL}/deadline-types", headers=headers)
    
    if types_response.status_code != 200:
        print(f"❌ Ошибка получения списка: {types_response.status_code}")
        return
    
    types = types_response.json()
    print(f"✅ Получено типов: {len(types)}")
    
    if not types:
        print("⚠️ Нет типов для тестирования")
        return
    
    # Выбираем первый тип для тестирования
    test_type = types[0]
    print(f"\n   Тестовый тип:")
    print(f"   ID: {test_type['id']}")
    print(f"   Название: {test_type['type_name']}")
    
    # 3. Попытка редактирования
    print(f"\n3️⃣ Попытка редактирования типа {test_type['id']}")
    update_data = {
        "type_name": test_type['type_name'],
        "description": test_type.get('description'),
        "is_active": test_type.get('is_active', True)
    }
    
    update_response = requests.put(
        f"{BASE_URL}/deadline-types/{test_type['id']}",
        headers=headers,
        json=update_data
    )
    
    if update_response.status_code == 200:
        print(f"✅ Редактирование разрешено для роли '{user_role}'")
    elif update_response.status_code == 403:
        error_data = update_response.json()
        print(f"❌ Редактирование запрещено для роли '{user_role}'")
        print(f"   Ошибка: {error_data.get('detail')}")
    else:
        print(f"⚠️ Неожиданный код ответа: {update_response.status_code}")
        print(f"   {update_response.text}")
    
    # 4. Попытка удаления (создадим тестовый тип)
    print(f"\n4️⃣ Создание тестового типа для проверки удаления")
    create_data = {
        "type_name": f"ТЕСТ_УДАЛЕНИЯ_{username}",
        "description": "Временный тип для теста",
        "is_active": True
    }
    
    create_response = requests.post(
        f"{BASE_URL}/deadline-types",
        headers=headers,
        json=create_data
    )
    
    if create_response.status_code == 201:
        created_type = create_response.json()
        print(f"✅ Тестовый тип создан: ID {created_type['id']}")
        
        # Попытка удаления
        print(f"\n5️⃣ Попытка удаления типа {created_type['id']}")
        delete_response = requests.delete(
            f"{BASE_URL}/deadline-types/{created_type['id']}",
            headers=headers
        )
        
        if delete_response.status_code == 204:
            print(f"✅ Удаление разрешено для роли '{user_role}'")
        elif delete_response.status_code == 403:
            error_data = delete_response.json()
            print(f"❌ Удаление запрещено для роли '{user_role}'")
            print(f"   Ошибка: {error_data.get('detail')}")
        elif delete_response.status_code == 400:
            error_data = delete_response.json()
            print(f"⚠️ Удаление не разрешено из-за бизнес-логики")
            print(f"   Ошибка: {error_data.get('detail')}")
        else:
            print(f"⚠️ Неожиданный код ответа: {delete_response.status_code}")
            print(f"   {delete_response.text}")
    elif create_response.status_code == 403:
        error_data = create_response.json()
        print(f"❌ Создание запрещено для роли '{user_role}'")
        print(f"   Ошибка: {error_data.get('detail')}")
    else:
        print(f"⚠️ Не удалось создать тестовый тип: {create_response.status_code}")
        print(f"   {create_response.text}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_deadline_types_access()
