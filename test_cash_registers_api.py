# -*- coding: utf-8 -*-
"""
Скрипт для быстрого тестирования API кассовых аппаратов
"""
import requests
import json
from datetime import datetime, timedelta

# Настройки
BASE_URL = "http://localhost:8001"
USERNAME = "admin"
PASSWORD = "admin123"

def print_section(title):
    """Печать заголовка раздела"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def get_auth_token():
    """Получить токен авторизации"""
    print_section("🔐 АВТОРИЗАЦИЯ")
    url = f"{BASE_URL}/api/auth/login"
    data = {"username": USERNAME, "password": PASSWORD}
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Успешная авторизация!")
        print(f"   Token: {token[:50]}...")
        return token
    else:
        print(f"❌ Ошибка авторизации: {response.status_code}")
        print(response.text)
        return None

def test_list_cash_registers(token):
    """Тест: Получение списка касс"""
    print_section("📋 СПИСОК КАССОВЫХ АППАРАТОВ")
    url = f"{BASE_URL}/api/cash-registers?page=1&limit=3"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Получено касс: {data['total']}")
        print(f"   Страница: {data['page']}, Лимит: {data['limit']}")
        print(f"\n   Первые 3 кассы:")
        for reg in data['cash_registers'][:3]:
            print(f"   - ID {reg['id']}: {reg['register_name']} (SN: {reg['serial_number']})")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return False

def test_get_cash_register_details(token, register_id=19):
    """Тест: Получение деталей кассы"""
    print_section(f"🔍 ДЕТАЛИ КАССЫ ID={register_id}")
    url = f"{BASE_URL}/api/cash-registers/{register_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Касса: {data['register_name']}")
        print(f"   Владелец: {data['user_name']}")
        print(f"   Заводской номер: {data['serial_number']}")
        print(f"   ФН: {data['fiscal_drive_number']}")
        print(f"   Адрес: {data['installation_address']}")
        print(f"\n   Дедлайны ({len(data['deadlines'])} шт.):")
        for dl in data['deadlines']:
            status_icon = {"red": "🔴", "orange": "🟠", "yellow": "🟡", "green": "🟢"}.get(dl['status_color'], "⚪")
            print(f"   {status_icon} {dl['deadline_type_name']}: {dl['expiration_date']} ({dl['days_until_expiration']} дн.)")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return False

def test_get_user_full_details(token, user_id=3):
    """Тест: Получение полных деталей клиента"""
    print_section(f"👤 ПОЛНЫЕ ДЕТАЛИ КЛИЕНТА ID={user_id}")
    url = f"{BASE_URL}/api/users/{user_id}/full-details"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Клиент: {data['name']}")
        print(f"   ИНН: {data['inn']}")
        print(f"   Кассовых аппаратов: {len(data['cash_registers'])}")
        print(f"   Дедлайнов по кассам: {len(data['register_deadlines'])}")
        print(f"   Общих дедлайнов: {len(data['general_deadlines'])}")
        
        print(f"\n   Кассы:")
        for reg in data['cash_registers']:
            print(f"   - {reg['register_name']} (SN: {reg['serial_number']})")
        
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return False

def test_create_cash_register(token):
    """Тест: Создание новой кассы"""
    print_section("➕ СОЗДАНИЕ НОВОЙ КАССЫ")
    url = f"{BASE_URL}/api/cash-registers"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Генерируем уникальный серийный номер на основе времени
    timestamp = datetime.now().strftime("%H%M%S")
    serial = f"TEST{timestamp}"
    
    data = {
        "user_id": 3,
        "serial_number": serial,
        "fiscal_drive_number": f"FN{timestamp}",
        "register_name": f"Тестовая касса {timestamp}",
        "installation_address": "г. Москва, ул. Тестовая, д. 1"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Касса создана!")
        print(f"   ID: {result['id']}")
        print(f"   Сообщение: {result['message']}")
        return result['id']
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)
        return None

def test_update_cash_register(token, register_id):
    """Тест: Обновление кассы"""
    print_section(f"✏️ ОБНОВЛЕНИЕ КАССЫ ID={register_id}")
    url = f"{BASE_URL}/api/cash-registers/{register_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "register_name": "Обновленная тестовая касса",
        "installation_address": "г. Москва, ул. Новая, д. 2"
    }
    
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Касса обновлена!")
        print(f"   Сообщение: {result['message']}")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return False

def test_delete_cash_register(token, register_id):
    """Тест: Удаление кассы (мягкое)"""
    print_section(f"🗑️ УДАЛЕНИЕ КАССЫ ID={register_id}")
    url = f"{BASE_URL}/api/cash-registers/{register_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:  # Изменено с 204 на 200
        result = response.json()
        print(f"✅ Касса успешно удалена (деактивирована)!")
        print(f"   Сообщение: {result['message']}")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return False

def main():
    """Основная функция тестирования"""
    print("\n" + "🚀 ЗАПУСК ТЕСТИРОВАНИЯ API КАССОВЫХ АППАРАТОВ".center(60))
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Получаем токен
    token = get_auth_token()
    if not token:
        print("\n❌ Невозможно продолжить без токена авторизации")
        return
    
    # Счетчики тестов
    passed = 0
    failed = 0
    
    # Тест 1: Список касс
    if test_list_cash_registers(token):
        passed += 1
    else:
        failed += 1
    
    # Тест 2: Детали кассы
    if test_get_cash_register_details(token, register_id=19):
        passed += 1
    else:
        failed += 1
    
    # Тест 3: Полные детали клиента
    if test_get_user_full_details(token, user_id=3):
        passed += 1
    else:
        failed += 1
    
    # Тест 4: Создание кассы
    new_register_id = test_create_cash_register(token)
    if new_register_id:
        passed += 1
        
        # Тест 5: Обновление созданной кассы
        if test_update_cash_register(token, new_register_id):
            passed += 1
        else:
            failed += 1
        
        # Тест 6: Удаление созданной кассы
        if test_delete_cash_register(token, new_register_id):
            passed += 1
        else:
            failed += 1
    else:
        failed += 3  # Пропустили 3 теста
    
    # Итоги
    print_section("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    total = passed + failed
    print(f"   Всего тестов: {total}")
    print(f"   ✅ Пройдено: {passed}")
    print(f"   ❌ Провалено: {failed}")
    print(f"   Успешность: {(passed/total*100):.1f}%")
    print(f"\nВремя завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
