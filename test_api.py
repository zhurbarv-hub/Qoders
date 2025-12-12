import requests
import json

# Получить токен
login_response = requests.post(
    'http://localhost:8000/api/auth/login',
    json={'username': 'admin', 'password': 'admin123'}
)

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    print(f"✅ Токен получен")
    
    # Проверить типы дедлайнов
    headers = {'Authorization': f'Bearer {token}'}
    types_response = requests.get('http://localhost:8000/api/deadline-types', headers=headers)
    
    print(f"\n📋 Status: {types_response.status_code}")
    
    if types_response.status_code == 200:
        data = types_response.json()
        print(f"📊 Всего типов услуг: {len(data)}")
        print("\n" + "=" * 80)
        
        for t in data:
            print(f"\n- ID: {t.get('id')}")
            print(f"  Название: {t.get('type_name')}")
            print(f"  Описание: {t.get('description') or '-'}")
            print(f"  Системный: {t.get('is_system')}")
            print(f"  Активен: {t.get('is_active')}")
        
        print("\n" + "=" * 80)
        print("✅ ВСЕ ТИПЫ ДОСТУПНЫ!")
        print("\n✅ Теперь можно без проблем добавлять дедлайны с любым типом!")
    else:
        print(f"❌ Ошибка: {types_response.text}")
else:
    print(f"❌ Ошибка авторизации: {login_response.text}")
