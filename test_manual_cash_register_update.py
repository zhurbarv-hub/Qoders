# -*- coding: utf-8 -*-
"""
Тест API обновления кассы с отслеживанием создания дедлайнов
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api"

def test_cash_register_update():
    """Тестирование обновления кассы с созданием дедлайнов"""
    
    print("\n" + "="*70)
    print("ТЕСТ: Обновление кассы с автоматическим созданием дедлайнов")
    print("="*70 + "\n")
    
    # 1. Авторизация
    username = input("Введите логин (admin): ") or "admin"
    password = input("Введите пароль: ") or "admin123"
    
    print(f"\n1️⃣ Авторизация...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Ошибка авторизации: {login_response.status_code}")
        print(f"   {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    print(f"✅ Авторизация успешна")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Получить список касс
    print(f"\n2️⃣ Получение списка касс...")
    registers_response = requests.get(f"{BASE_URL}/cash-registers", headers=headers)
    
    if registers_response.status_code != 200:
        print(f"❌ Ошибка получения списка касс: {registers_response.status_code}")
        return
    
    registers = registers_response.json()
    if not registers:
        print("❌ Нет касс для тестирования")
        return
    
    # Выбираем первую кассу
    test_register = registers[0]
    register_id = test_register['id']
    print(f"✅ Выбрана касса: ID={register_id}, Название: {test_register.get('register_name')}")
    
    # 3. Получить текущее состояние кассы
    print(f"\n3️⃣ Получение текущего состояния кассы...")
    register_response = requests.get(f"{BASE_URL}/cash-registers/{register_id}", headers=headers)
    
    if register_response.status_code != 200:
        print(f"❌ Ошибка получения кассы: {register_response.status_code}")
        return
    
    current_register = register_response.json()
    print(f"✅ Текущее состояние:")
    print(f"   Дата замены ФН: {current_register.get('fn_replacement_date') or 'не установлена'}")
    print(f"   Дата продления ОФД: {current_register.get('ofd_renewal_date') or 'не установлена'}")
    
    # 4. Подготовить новые даты
    new_fn_date = (date.today() + timedelta(days=45)).isoformat()
    new_ofd_date = (date.today() + timedelta(days=60)).isoformat()
    
    print(f"\n4️⃣ Подготовка новых дат:")
    print(f"   Новая дата замены ФН: {new_fn_date}")
    print(f"   Новая дата продления ОФД: {new_ofd_date}")
    
    # 5. Обновить кассу
    update_data = {
        "fn_replacement_date": new_fn_date,
        "ofd_renewal_date": new_ofd_date
    }
    
    print(f"\n5️⃣ Отправка запроса на обновление кассы...")
    print(f"   URL: {BASE_URL}/cash-registers/{register_id}")
    print(f"   Данные: {json.dumps(update_data, ensure_ascii=False, indent=2)}")
    
    update_response = requests.put(
        f"{BASE_URL}/cash-registers/{register_id}",
        headers=headers,
        json=update_data
    )
    
    print(f"\n   Код ответа: {update_response.status_code}")
    
    if update_response.status_code != 200:
        print(f"❌ Ошибка обновления кассы!")
        print(f"   Ответ сервера: {update_response.text}")
        return
    
    updated_register = update_response.json()
    print(f"✅ Касса успешно обновлена:")
    print(f"   Дата замены ФН: {updated_register.get('fn_replacement_date')}")
    print(f"   Дата продления ОФД: {updated_register.get('ofd_renewal_date')}")
    
    # 6. Проверить созданные дедлайны
    print(f"\n6️⃣ Проверка созданных дедлайнов...")
    
    # Ждем немного для завершения транзакции
    import time
    time.sleep(0.5)
    
    deadlines_response = requests.get(
        f"{BASE_URL}/deadlines?cash_register_id={register_id}",
        headers=headers
    )
    
    if deadlines_response.status_code != 200:
        print(f"❌ Ошибка получения дедлайнов: {deadlines_response.status_code}")
        return
    
    deadlines_data = deadlines_response.json()
    deadlines = deadlines_data.get('deadlines', [])
    
    print(f"✅ Найдено дедлайнов для кассы: {len(deadlines)}")
    
    if deadlines:
        for dl in deadlines:
            print(f"\n   Дедлайн ID={dl.get('id')}:")
            print(f"     Тип: {dl.get('deadline_type', {}).get('type_name', 'Неизвестно')}")
            print(f"     Дата истечения: {dl.get('expiration_date')}")
            print(f"     Статус: {dl.get('status')}")
            print(f"     Примечание: {dl.get('notes', '')[:80]}...")
    else:
        print("\n   ⚠️ Дедлайны не найдены!")
        print("   Возможные причины:")
        print("   1. Веб-сервер не был перезапущен после исправления кода")
        print("   2. Типы дедлайнов отсутствуют в БД")
        print("   3. Произошла ошибка при создании (проверьте логи сервера)")
    
    # 7. Проверить типы дедлайнов
    print(f"\n7️⃣ Проверка доступных типов дедлайнов...")
    types_response = requests.get(f"{BASE_URL}/deadline-types", headers=headers)
    
    if types_response.status_code == 200:
        types = types_response.json()
        print(f"✅ Найдено типов дедлайнов: {len(types)}")
        
        fn_type = next((t for t in types if t['type_name'] == "Замена ФН"), None)
        ofd_type = next((t for t in types if t['type_name'] == "Продление договора ОФД"), None)
        
        if fn_type:
            print(f"   ✅ Тип 'Замена ФН' найден: ID={fn_type['id']}")
        else:
            print(f"   ❌ Тип 'Замена ФН' НЕ найден")
        
        if ofd_type:
            print(f"   ✅ Тип 'Продление договора ОФД' найден: ID={ofd_type['id']}")
        else:
            print(f"   ❌ Тип 'Продление договора ОФД' НЕ найден")
            print(f"   Доступные типы:")
            for t in types:
                print(f"     - {t['type_name']}")
    
    print("\n" + "="*70)
    print("РЕКОМЕНДАЦИИ:")
    print("="*70)
    print("1. Убедитесь, что веб-сервер был перезапущен после исправления кода")
    print("2. Проверьте логи веб-сервера на наличие ошибок")
    print("3. Убедитесь, что типы 'Замена ФН' и 'Продление договора ОФД' существуют")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_cash_register_update()
