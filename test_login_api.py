#!/usr/bin/env python3
"""
Тестирование API логина
"""
import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

import json
import requests

# Данные для входа
login_data = {
    "username": "Eliseev",
    "password": "7ywyrfrwei"
}

print(f"Отправка запроса на логин...")
print(f"URL: http://localhost:8000/api/auth/login")
print(f"Data: {json.dumps(login_data, indent=2)}\n")

try:
    response = requests.post(
        "http://localhost:8000/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ УСПЕШНЫЙ ВХОД!")
        print(f"Access Token: {data['access_token'][:50]}...")
        print(f"User: {json.dumps(data['user'], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ ОШИБКА: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error Details: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response Text: {response.text}")
            
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()
