#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования работы веб-интерфейса дашборда
"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_login():
    """Тест авторизации"""
    print("=" * 60)
    print("ТЕСТ 1: Авторизация")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Авторизация успешна")
        print(f"  Token: {data['access_token'][:50]}...")
        print(f"  User: {data['user']['username']} ({data['user']['role']})")
        return data['access_token']
    else:
        print(f"✗ Ошибка авторизации: {response.text}")
        return None

def test_dashboard_summary(token):
    """Тест получения статистики дашборда"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Получение статистики дашборда")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/dashboard/summary", headers=headers)
    
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Статистика получена")
        print(f"\n📊 Клиенты:")
        print(f"  • Всего: {data['total_clients']}")
        print(f"  • Активных: {data['active_clients']}")
        print(f"\n📅 Дедлайны:")
        print(f"  • Всего: {data['total_deadlines']}")
        print(f"\n🚦 Статусы:")
        print(f"  • Зелёный (>14 дн.): {data['status_breakdown']['green']}")
        print(f"  • Жёлтый (7-14 дн.): {data['status_breakdown']['yellow']}")
        print(f"  • Красный (0-7 дн.): {data['status_breakdown']['red']}")
        print(f"  • Просрочено: {data['status_breakdown']['expired']}")
        print(f"\n🚨 Срочных дедлайнов: {len(data['urgent_deadlines'])}")
        
        if data['urgent_deadlines']:
            print("\nПервые 3 срочных дедлайна:")
            for deadline in data['urgent_deadlines'][:3]:
                print(f"  • {deadline['client_name']}: {deadline['deadline_type']} - {deadline['expiration_date']} ({deadline['days_remaining']} дн.)")
        return True
    else:
        print(f"✗ Ошибка получения статистики: {response.text}")
        return False

def test_dashboard_stats_by_type(token):
    """Тест получения статистики по типам"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Статистика по типам услуг")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/dashboard/stats/by-type", headers=headers)
    
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Статистика по типам получена")
        print(f"\n📈 Распределение по типам услуг:")
        for item in data:
            print(f"  • {item['deadline_type']}: {item['count']} дедлайнов")
        return True
    else:
        print(f"✗ Ошибка получения статистики: {response.text}")
        return False

def test_static_files():
    """Тест доступности статических файлов"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Доступность веб-интерфейса")
    print("=" * 60)
    
    files = [
        "/login.html",
        "/dashboard.html",
        "/static/js/auth.js",
        "/static/js/dashboard.js",
        "/static/css/styles.css"
    ]
    
    for file_path in files:
        response = requests.get(f"http://localhost:8000{file_path}")
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} {file_path}: {response.status_code}")

if __name__ == "__main__":
    import sys
    import io
    # Устанавливаем UTF-8 для вывода в консоль Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "ТЕСТИРОВАНИЕ ВЕБ-ИНТЕРФЕЙСА ДАШБОРДА" + " " * 11 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    try:
        # Тест 1: Авторизация
        token = test_login()
        if not token:
            print("\n❌ Тесты прерваны: не удалось авторизоваться")
            exit(1)
        
        # Тест 2: Статистика дашборда
        test_dashboard_summary(token)
        
        # Тест 3: Статистика по типам
        test_dashboard_stats_by_type(token)
        
        # Тест 4: Статические файлы
        test_static_files()
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        print("=" * 60)
        print("\nДашборд доступен по адресу: http://localhost:8000/dashboard.html")
        print("Для авторизации используйте: admin / admin123\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ОШИБКА: Не удалось подключиться к серверу")
        print("Убедитесь, что FastAPI сервер запущен на http://localhost:8000")
        print("Для запуска используйте: start_api.bat\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {e}\n")
        exit(1)
