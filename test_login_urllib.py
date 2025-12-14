#!/usr/bin/env python3
"""
Тестирование API логина через urllib
"""
import json
import urllib.request
import urllib.error

# Данные для входа
login_data = {
    "username": "Eliseev",
    "password": "7ywyrfrwei"
}

url = "http://localhost:8000/api/auth/login"
data = json.dumps(login_data).encode('utf-8')
headers = {'Content-Type': 'application/json'}

print(f"Отправка запроса на логин...")
print(f"URL: {url}")
print(f"Data: {login_data}\n")

try:
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        status = response.status
        body = response.read().decode('utf-8')
        
        print(f"Status Code: {status}")
        
        if status == 200:
            result = json.loads(body)
            print("✅ УСПЕШНЫЙ ВХОД!")
            print(f"Access Token: {result['access_token'][:50]}...")
            print(f"User: {json.dumps(result['user'], indent=2, ensure_ascii=False)}")
        else:
            print(f"Response: {body}")
            
except urllib.error.HTTPError as e:
    print(f"❌ HTTP Error: {e.code}")
    error_body = e.read().decode('utf-8')
    print(f"Error Response: {error_body}")
    try:
        error_data = json.loads(error_body)
        print(f"Parsed Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
    except:
        pass
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()
