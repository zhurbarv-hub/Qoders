# -*- coding: utf-8 -*-
"""
Тестирование функциональности автоматических дедлайнов для кассовых аппаратов
"""
import requests
from datetime import date, timedelta
import json

API_BASE = "http://localhost:8000/api"

# Получить токен авторизации
def get_auth_token(username="admin", password="admin123"):
    """Получить JWT токен"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Ошибка авторизации: {response.status_code}")
        print(response.text)
        return None

def test_create_cash_register_with_dates():
    """Тест 1: Создание кассы с датами - должны автоматически создаться дедлайны"""
    print("\n" + "="*80)
    print("ТЕСТ 1: Создание кассового аппарата с датами дедлайнов")
    print("="*80)
    
    token = get_auth_token()
    if not token:
        print("❌ Не удалось получить токен")
        return False, None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Получаем первого клиента
    users_response = requests.get(f"{API_BASE}/users", headers=headers)
    if users_response.status_code != 200:
        print(f"❌ Ошибка получения списка пользователей: {users_response.status_code}")
        return False, None
    
    users_data = users_response.json()
    print(f"Отладка - тип данных пользователей: {type(users_data)}")
    
    # Обрабатываем разные форматы ответа
    if isinstance(users_data, dict):
        users = users_data.get('users', users_data.get('data', []))
    else:
        users = users_data
    
    if not users or len(users) == 0:
        print("❌ Нет пользователей в системе")
        return False, None
    
    user_id = users[0]["id"]
    print(f"✓ Используем пользователя ID={user_id}")
    
    # Создаем кассу с датами
    from datetime import datetime
    today = date.today()
    fn_date = today + timedelta(days=45)
    ofd_date = today + timedelta(days=60)
    unique_suffix = datetime.now().strftime('%Y%m%d%H%M%S')
    
    cash_register_data = {
        "user_id": user_id,
        "serial_number": f"TEST-{unique_suffix}",
        "fiscal_drive_number": f"FN{unique_suffix}",
        "register_name": "Тестовая касса с дедлайнами",
        "installation_address": "Тестовый адрес",
        "notes": "Создано для тестирования автоматических дедлайнов",
        "fn_replacement_date": fn_date.isoformat(),
        "ofd_renewal_date": ofd_date.isoformat()
    }
    
    print(f"\n📤 Отправка запроса на создание кассы...")
    print(f"   - Дата замены ФН: {fn_date}")
    print(f"   - Дата продления ОФД: {ofd_date}")
    
    response = requests.post(
        f"{API_BASE}/cash-registers",
        headers=headers,
        json=cash_register_data
    )
    
    if response.status_code != 201:
        print(f"❌ Ошибка создания кассы: {response.status_code}")
        print(response.text)
        return False, None
    
    register = response.json()
    register_id = register["id"]
    print(f"✓ Касса создана успешно, ID={register_id}")
    print(f"  fn_replacement_date: {register.get('fn_replacement_date')}")
    print(f"  ofd_renewal_date: {register.get('ofd_renewal_date')}")
    
    # Проверяем, что созданы дедлайны
    print(f"\n🔍 Проверка автоматически созданных дедлайнов...")
    deadlines_response = requests.get(
        f"{API_BASE}/deadlines?cash_register_id={register_id}",
        headers=headers
    )
    
    if deadlines_response.status_code != 200:
        print(f"❌ Ошибка получения дедлайнов: {deadlines_response.status_code}")
        return False, None
    
    deadlines_data = deadlines_response.json()
    deadlines = deadlines_data.get("deadlines", [])
    
    print(f"✓ Найдено дедлайнов для кассы: {len(deadlines)}")
    
    fn_deadline_found = False
    ofd_deadline_found = False
    
    for dl in deadlines:
        dt_name = dl['deadline_type'].get('type_name', dl['deadline_type'].get('name', 'Unknown'))
        print(f"\n  📅 Дедлайн: {dt_name}")
        print(f"     Дата истечения: {dl['expiration_date']}")
        print(f"     Статус: {dl['status']}")
        print(f"     Примечание: {dl.get('notes', 'нет')}")
        
        if dt_name == "Замена ФН":
            fn_deadline_found = True
            if dl['expiration_date'] == fn_date.isoformat():
                print(f"     ✓ Дата совпадает с указанной!")
        elif "продлен" in dt_name.lower():
            ofd_deadline_found = True
            if dl['expiration_date'] == ofd_date.isoformat():
                print(f"     ✓ Дата совпадает с указанной!")
    
    print(f"\n📊 Результаты:")
    print(f"   Дедлайн 'Замена ФН': {'✓ Создан' if fn_deadline_found else '❌ НЕ создан'}")
    print(f"   Дедлайн 'Продление ОФД': {'✓ Создан' if ofd_deadline_found else '❌ НЕ создан'}")
    
    success = fn_deadline_found and ofd_deadline_found
    
    if success:
        print(f"\n✅ ТЕСТ 1 ПРОЙДЕН: Дедлайны созданы автоматически!")
    else:
        print(f"\n❌ ТЕСТ 1 НЕ ПРОЙДЕН: Не все дедлайны созданы")
    
    return success, register_id

def test_update_cash_register_dates(register_id):
    """Тест 2: Обновление дат в кассе - должны обновиться дедлайны"""
    print("\n" + "="*80)
    print("ТЕСТ 2: Обновление дат дедлайнов в существующей кассе")
    print("="*80)
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Получаем текущую кассу
    response = requests.get(f"{API_BASE}/cash-registers/{register_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Ошибка получения кассы: {response.status_code}")
        return False
    
    register = response.json()
    old_fn_date = register.get("fn_replacement_date")
    print(f"✓ Текущая дата замены ФН: {old_fn_date}")
    
    # Обновляем дату замены ФН
    new_fn_date = (date.today() + timedelta(days=90)).isoformat()
    
    update_data = {
        "fn_replacement_date": new_fn_date
    }
    
    print(f"📤 Обновление даты замены ФН: {old_fn_date} → {new_fn_date}")
    
    response = requests.put(
        f"{API_BASE}/cash-registers/{register_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code != 200:
        print(f"❌ Ошибка обновления кассы: {response.status_code}")
        print(response.text)
        return False
    
    updated_register = response.json()
    print(f"✓ Касса обновлена, новая дата: {updated_register.get('fn_replacement_date')}")
    
    # Проверяем обновление дедлайна
    print(f"\n🔍 Проверка обновления дедлайна...")
    deadlines_response = requests.get(
        f"{API_BASE}/deadlines?cash_register_id={register_id}",
        headers=headers
    )
    
    if deadlines_response.status_code != 200:
        print(f"❌ Ошибка получения дедлайнов")
        return False
    
    deadlines = deadlines_response.json().get("deadlines", [])
    
    fn_deadline_updated = False
    for dl in deadlines:
        dt_name = dl['deadline_type'].get('type_name', dl['deadline_type'].get('name', 'Unknown'))
        if dt_name == "Замена ФН" and dl['status'] == 'active':
            print(f"  📅 Найден дедлайн 'Замена ФН':")
            print(f"     Дата истечения: {dl['expiration_date']}")
            if dl['expiration_date'] == new_fn_date:
                print(f"     ✓ Дата успешно обновлена!")
                fn_deadline_updated = True
            else:
                print(f"     ❌ Дата НЕ обновлена (ожидалось {new_fn_date})")
    
    if fn_deadline_updated:
        print(f"\n✅ ТЕСТ 2 ПРОЙДЕН: Дедлайн обновлен автоматически!")
        return True
    else:
        print(f"\n❌ ТЕСТ 2 НЕ ПРОЙДЕН: Дедлайн не обновлен")
        return False

if __name__ == "__main__":
    print("╔" + "="*78 + "╗")
    print("║  ТЕСТИРОВАНИЕ АВТОМАТИЧЕСКИХ ДЕДЛАЙНОВ ДЛЯ КАССОВЫХ АППАРАТОВ          ║")
    print("╚" + "="*78 + "╝")
    
    try:
        # Тест 1: Создание кассы с датами
        test1_result, register_id = test_create_cash_register_with_dates()
        
        if test1_result:
            # Тест 2: Обновление дат
            test2_result = test_update_cash_register_dates(register_id)
        else:
            test2_result = False
            print("\n⏭️  Тест 2 пропущен из-за ошибки в Тесте 1")
        
        # Итоги
        print("\n" + "="*80)
        print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("="*80)
        print(f"Тест 1 (Создание с датами):    {'✅ ПРОЙДЕН' if test1_result else '❌ НЕ ПРОЙДЕН'}")
        print(f"Тест 2 (Обновление дат):       {'✅ ПРОЙДЕН' if test2_result else '❌ НЕ ПРОЙДЕН'}")
        print("="*80)
        
        if test1_result and test2_result:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
            
    except Exception as e:
        print(f"\n❌ Ошибка выполнения тестов: {e}")
        import traceback
        traceback.print_exc()
