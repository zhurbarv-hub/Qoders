#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка API дашборда"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Логин
login_resp = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "Eliseev", "password": "password123"}
)

if login_resp.status_code != 200:
    print(f"Ошибка логина: {login_resp.status_code}")
    print(login_resp.text)
    exit(1)

token = login_resp.json()["access_token"]
print(f"✓ Токен получен")

# Получение статистики
headers = {"Authorization": f"Bearer {token}"}
stats_resp = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)

if stats_resp.status_code != 200:
    print(f"Ошибка получения статистики: {stats_resp.status_code}")
    print(stats_resp.text)
    exit(1)

stats = stats_resp.json()
print(f"\n📊 Статистика дашборда:")
print(json.dumps(stats, indent=2, ensure_ascii=False))

print(f"\n🔍 Важные показатели:")
print(f"  - Всего клиентов: {stats.get('total_clients', 0)}")
print(f"  - Активных клиентов: {stats.get('active_clients', 0)}")
print(f"  - Всего касс: {stats.get('total_cash_registers', 0)}")
print(f"  - Активных дедлайнов: {stats.get('active_deadlines', 0)}")
