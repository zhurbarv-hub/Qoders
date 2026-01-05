#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тест статистики касс на дашборде"""

import requests
import json

BASE_URL = "http://185.185.71.248:8080/api"

def test_cash_register_stats():
    """Тест добавления статистики по кассам"""
    
    # 1. Авторизация
    print("1️⃣ Авторизация...")
    login_data = {
        "username": "eliseev",
        "password": "eliseev"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Статус авторизации: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Ошибка авторизации: {response.text}")
        return
    
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"✅ Токен получен: {access_token[:50]}...")
    
    # 2. Получение статистики дашборда
    print("\n2️⃣ Получение статистики дашборда...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    print(f"Статус запроса: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Ошибка получения статистики: {response.text}")
        return
    
    stats = response.json()
    print("✅ Статистика получена:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 3. Проверка наличия поля total_cash_registers
    print("\n3️⃣ Проверка поля total_cash_registers...")
    if 'total_cash_registers' in stats:
        print(f"✅ Поле total_cash_registers присутствует: {stats['total_cash_registers']}")
    else:
        print("❌ Поле total_cash_registers ОТСУТСТВУЕТ!")
        print("Доступные поля:", list(stats.keys()))
        return
    
    # 4. Вывод всех статистик
    print("\n4️⃣ Итоговая статистика:")
    print(f"  📊 Всего клиентов: {stats['total_clients']}")
    print(f"  ✅ Активных клиентов: {stats['active_clients']}")
    print(f"  💰 Всего касс: {stats['total_cash_registers']}")
    print(f"  📅 Всего дедлайнов: {stats['total_deadlines']}")
    print(f"  ⏰ Активных дедлайнов: {stats['active_deadlines']}")
    print(f"  🟢 Норма (>14 дней): {stats['status_green']}")
    print(f"  🟡 Внимание (7-14 дней): {stats['status_yellow']}")
    print(f"  🔴 Срочно (0-7 дней): {stats['status_red']}")
    print(f"  ⚫ Просрочено: {stats['status_expired']}")
    
    print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")

if __name__ == "__main__":
    test_cash_register_stats()
