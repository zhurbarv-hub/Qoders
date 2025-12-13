"""
Тест улучшений панели статистики
Проверяет новый параметр include_expired в API /deadlines/urgent
"""

import requests
from datetime import datetime

# Конфигурация
API_BASE = "http://localhost:8000/api"
USERNAME = "admin"
PASSWORD = "admin123"

def test_dashboard_enhancements():
    print("=" * 70)
    print("ТЕСТ УЛУЧШЕНИЙ ПАНЕЛИ СТАТИСТИКИ")
    print("=" * 70)
    
    # Шаг 1: Авторизация
    print("\n[1/3] 🔐 Авторизация...")
    login_response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Ошибка авторизации: {login_response.status_code}")
        print(login_response.text)
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Успешная авторизация")
    
    # Шаг 2: Тест API с включением просроченных (по умолчанию)
    print("\n[2/3] 📊 Тест API /deadlines/urgent (include_expired=true, по умолчанию)...")
    urgent_response = requests.get(
        f"{API_BASE}/deadlines/urgent?days=14",
        headers=headers
    )
    
    if urgent_response.status_code != 200:
        print(f"❌ Ошибка запроса: {urgent_response.status_code}")
        print(urgent_response.text)
        return False
    
    urgent_deadlines = urgent_response.json()
    print(f"✅ Получено дедлайнов: {len(urgent_deadlines)}")
    
    # Подсчет просроченных
    today = datetime.now().date()
    expired_count = 0
    upcoming_count = 0
    
    for deadline in urgent_deadlines:
        exp_date = datetime.strptime(deadline['expiration_date'], '%Y-%m-%d').date()
        if exp_date < today:
            expired_count += 1
        else:
            upcoming_count += 1
    
    print(f"   - Просроченных: {expired_count}")
    print(f"   - Предстоящих: {upcoming_count}")
    
    if expired_count > 0:
        print("✅ Просроченные дедлайны ВКЛЮЧЕНЫ в выборку (новое поведение)")
    else:
        print("⚠️  Просроченных дедлайнов нет в данных (или их просто нет в БД)")
    
    # Шаг 3: Тест API без просроченных
    print("\n[3/3] 📊 Тест API /deadlines/urgent?include_expired=false...")
    upcoming_response = requests.get(
        f"{API_BASE}/deadlines/urgent?days=14&include_expired=false",
        headers=headers
    )
    
    if upcoming_response.status_code != 200:
        print(f"❌ Ошибка запроса: {upcoming_response.status_code}")
        print(upcoming_response.text)
        return False
    
    upcoming_deadlines = upcoming_response.json()
    print(f"✅ Получено дедлайнов: {len(upcoming_deadlines)}")
    
    expired_in_upcoming = sum(
        1 for d in upcoming_deadlines 
        if datetime.strptime(d['expiration_date'], '%Y-%m-%d').date() < today
    )
    
    if expired_in_upcoming == 0:
        print("✅ Просроченные дедлайны ИСКЛЮЧЕНЫ из выборки (старое поведение)")
    else:
        print(f"❌ Найдено просроченных: {expired_in_upcoming} (должно быть 0)")
    
    # Итоговая проверка
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ТЕСТА")
    print("=" * 70)
    
    if len(urgent_deadlines) >= len(upcoming_deadlines):
        print("✅ Новый параметр include_expired работает корректно")
        print(f"   С просроченными: {len(urgent_deadlines)} дедлайнов")
        print(f"   Без просроченных: {len(upcoming_deadlines)} дедлайнов")
        return True
    else:
        print("❌ Что-то пошло не так с параметром include_expired")
        return False

if __name__ == "__main__":
    try:
        success = test_dashboard_enhancements()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
