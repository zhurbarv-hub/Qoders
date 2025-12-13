# -*- coding: utf-8 -*-
"""
Тест удаления типа услуги через API
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

def test_delete_deadline_type():
    print("=" * 80)
    print("ТЕСТ УДАЛЕНИЯ ТИПА УСЛУГИ")
    print("=" * 80)
    
    # 1. Авторизация
    print("\n[1/4] 🔐 Авторизация...")
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Ошибка авторизации: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("✅ Успешная авторизация")
    
    # 2. Получить список типов услуг
    print("\n[2/4] 📋 Получение списка типов услуг...")
    response = requests.get(f"{API_BASE_URL}/api/deadline-types", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Ошибка получения типов: {response.status_code}")
        print(response.text)
        return
    
    types = response.json()
    print(f"✅ Всего типов: {len(types)}")
    
    if len(types) == 0:
        print("⚠️ Нет типов для удаления")
        return
    
    # Показать типы
    print("\nТипы услуг:")
    for t in types:
        print(f"  - ID {t['id']}: {t['type_name']} (активен: {t['is_active']})")
    
    # 3. Проверить дедлайны для первого типа
    test_type_id = types[0]['id']
    print(f"\n[3/4] 🔍 Проверка дедлайнов для типа ID {test_type_id}...")
    
    response = requests.get(
        f"{API_BASE_URL}/api/deadlines",
        headers=headers,
        params={"deadline_type_id": test_type_id, "page_size": 100}
    )
    
    if response.status_code == 200:
        deadlines_data = response.json()
        deadlines_count = len(deadlines_data.get("deadlines", []))
        print(f"✅ Найдено дедлайнов с этим типом: {deadlines_count}")
    else:
        print(f"⚠️ Не удалось получить дедлайны: {response.status_code}")
        deadlines_count = "неизвестно"
    
    # 4. Попытка удалить тип
    print(f"\n[4/4] 🗑️ Попытка удалить тип ID {test_type_id}...")
    print(f"      Тип: {types[0]['type_name']}")
    print(f"      Связанных дедлайнов: {deadlines_count}")
    
    confirm = input("\n⚠️ Продолжить удаление? (да/нет): ").strip().lower()
    if confirm not in ['да', 'yes', 'y', 'д']:
        print("❌ Отменено пользователем")
        return
    
    response = requests.delete(
        f"{API_BASE_URL}/api/deadline-types/{test_type_id}",
        headers=headers
    )
    
    print(f"\nСтатус ответа: {response.status_code}")
    
    if response.status_code == 204:
        print("✅ Тип услуги успешно удален!")
        
        # Проверка что тип удален
        response = requests.get(f"{API_BASE_URL}/api/deadline-types", headers=headers)
        new_types = response.json()
        print(f"✅ Осталось типов: {len(new_types)}")
        
    elif response.status_code == 400:
        print("❌ Ошибка 400 - Неверный запрос")
        print(f"Детали: {response.text}")
    elif response.status_code == 403:
        print("❌ Ошибка 403 - Недостаточно прав")
    elif response.status_code == 404:
        print("❌ Ошибка 404 - Тип не найден")
    elif response.status_code == 500:
        print("❌ Ошибка 500 - Внутренняя ошибка сервера")
        print(f"Детали: {response.text}")
    else:
        print(f"❌ Неожиданный статус: {response.status_code}")
        print(f"Ответ: {response.text}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        test_delete_deadline_type()
    except requests.exceptions.ConnectionError:
        print("\n❌ Не удается подключиться к серверу")
        print("Убедитесь, что сервер запущен на http://localhost:8000")
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
