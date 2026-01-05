#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест API database/backups
"""
import requests
import json

# URL API
API_URL = "http://185.185.71.248/api/database/backups"

# Токен (замените на реальный)
TOKEN = "YOUR_TOKEN_HERE"

try:
    response = requests.get(
        API_URL,
        headers={
            "Authorization": f"Bearer {TOKEN}"
        },
        timeout=10
    )
    
    print(f"Статус: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.ok:
        data = response.json()
        print("\n=== ДАННЫЕ ===")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"\nОшибка: {response.text}")
        
except Exception as e:
    print(f"Ошибка подключения: {e}")
