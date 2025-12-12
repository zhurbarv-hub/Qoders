"""
Тест Export API endpoints
"""
import asyncio
import aiohttp
from backend.config import settings

async def test_export_api():
    print("=" * 70)
    print("ТЕСТ EXPORT API")
    print("=" * 70)
    
    base_url = settings.web_api_base_url
    
    # 1. Получение токена
    print("\n1️⃣ Аутентификация...")
    async with aiohttp.ClientSession() as session:
        login_url = f"{base_url}/api/auth/login"
        
        async with session.post(login_url, json={
            "username": settings.bot_api_username,
            "password": settings.bot_api_password
        }) as response:
            if response.status == 200:
                data = await response.json()
                token = data.get('access_token')
                print(f"   ✅ Токен получен")
            else:
                text = await response.text()
                print(f"   ❌ Ошибка аутентификации: {response.status}")
                print(f"   {text}")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Тест экспорта клиентов в JSON
        print("\n2️⃣ Экспорт клиентов в JSON...")
        async with session.get(
            f"{base_url}/api/export/clients?format=json",
            headers=headers
        ) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type')
                content_disp = response.headers.get('Content-Disposition')
                data = await response.text()
                
                print(f"   ✅ Статус: {response.status}")
                print(f"   📄 Content-Type: {content_type}")
                print(f"   📎 Content-Disposition: {content_disp}")
                print(f"   📊 Размер данных: {len(data)} байт")
                
                # Показываем первые 200 символов
                print(f"\n   Начало файла:")
                print(f"   {data[:200]}...")
            else:
                text = await response.text()
                print(f"   ❌ Ошибка: {response.status}")
                print(f"   {text}")
        
        # 3. Тест экспорта клиентов в CSV
        print("\n3️⃣ Экспорт клиентов в CSV...")
        async with session.get(
            f"{base_url}/api/export/clients?format=csv",
            headers=headers
        ) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type')
                content_disp = response.headers.get('Content-Disposition')
                data = await response.text()
                
                print(f"   ✅ Статус: {response.status}")
                print(f"   📄 Content-Type: {content_type}")
                print(f"   📎 Content-Disposition: {content_disp}")
                print(f"   📊 Размер данных: {len(data)} байт")
                
                # Показываем первые 5 строк
                lines = data.split('\n')[:5]
                print(f"\n   Первые строки CSV:")
                for line in lines:
                    print(f"   {line}")
            else:
                text = await response.text()
                print(f"   ❌ Ошибка: {response.status}")
                print(f"   {text}")
        
        # 4. Тест экспорта дедлайнов в JSON
        print("\n4️⃣ Экспорт дедлайнов в JSON...")
        async with session.get(
            f"{base_url}/api/export/deadlines?format=json",
            headers=headers
        ) as response:
            if response.status == 200:
                content_disp = response.headers.get('Content-Disposition')
                data = await response.text()
                
                print(f"   ✅ Статус: {response.status}")
                print(f"   📎 {content_disp}")
                print(f"   📊 Размер: {len(data)} байт")
            else:
                text = await response.text()
                print(f"   ❌ Ошибка: {response.status}")
                print(f"   {text}")
        
        # 5. Тест экспорта дедлайнов в CSV
        print("\n5️⃣ Экспорт дедлайнов в CSV...")
        async with session.get(
            f"{base_url}/api/export/deadlines?format=csv",
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.text()
                lines = data.split('\n')[:3]
                
                print(f"   ✅ Статус: {response.status}")
                print(f"   📊 Размер: {len(data)} байт")
                print(f"\n   Заголовки CSV:")
                for line in lines:
                    print(f"   {line}")
            else:
                text = await response.text()
                print(f"   ❌ Ошибка: {response.status}")
                print(f"   {text}")
        
        # 6. Тест экспорта статистики
        print("\n6️⃣ Экспорт статистики в JSON...")
        async with session.get(
            f"{base_url}/api/export/statistics?format=json",
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.text()
                
                print(f"   ✅ Статус: {response.status}")
                print(f"   📊 Размер: {len(data)} байт")
                print(f"\n   Содержимое:")
                print(f"   {data[:500]}...")
            else:
                text = await response.text()
                print(f"   ❌ Ошибка: {response.status}")
                print(f"   {text}")
        
        # 7. Тест экспорта статистики в CSV
        print("\n7️⃣ Экспорт статистики в CSV...")
        async with session.get(
            f"{base_url}/api/export/statistics?format=csv",
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.text()
                lines = data.split('\n')[:15]
                
                print(f"   ✅ Статус: {response.status}")
                print(f"\n   Статистика:")
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
            else:
                text = await response.text()
                print(f"   ❌ Ошибка: {response.status}")
                print(f"   {text}")
        
        # 8. Тест фильтров
        print("\n8️⃣ Тест фильтров (только активные клиенты)...")
        async with session.get(
            f"{base_url}/api/export/clients?format=json&is_active=true",
            headers=headers
        ) as response:
            if response.status == 200:
                import json
                data = await response.text()
                parsed = json.loads(data)
                
                print(f"   ✅ Статус: {response.status}")
                print(f"   📊 Всего записей: {parsed.get('total_records', 0)}")
                print(f"   📅 Дата экспорта: {parsed.get('export_date', 'N/A')}")
            else:
                text = await response.text()
                print(f"   ❌ Ошибка: {response.status}")
                print(f"   {text}")
    
    print("\n" + "=" * 70)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(test_export_api())