"""Отладочная проверка конфигурации"""
import os
from pathlib import Path

print("=" * 60)
print("ДИАГНОСТИКА КОНФИГУРАЦИИ")
print("=" * 60)

# Проверка 1: Существует ли .env файл?
env_path = Path(".env")
print(f"\n1. Файл .env существует: {env_path.exists()}")
if env_path.exists():
    print(f"   Путь: {env_path.absolute()}")
    print(f"   Размер: {env_path.stat().st_size} байт")

# Проверка 2: Что в переменных окружения?
print("\n2. Переменные окружения:")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
admin_id = os.getenv("TELEGRAM_ADMIN_ID")
print(f"   TELEGRAM_BOT_TOKEN: {bot_token[:20] if bot_token else 'НЕ ЗАДАН'}...")
print(f"   TELEGRAM_ADMIN_ID: {admin_id if admin_id else 'НЕ ЗАДАН'}")

# Проверка 3: Загрузка через pydantic-settings
print("\n3. Загрузка через pydantic-settings:")
try:
    from backend.config import Settings
    
    # Проверим какие поля есть в классе
    print("   Поля в классе Settings:")
    for field_name in Settings.model_fields.keys():
        if "telegram" in field_name.lower() or "notification" in field_name.lower():
            print(f"      - {field_name}")
    
    # Попытка создать экземпляр
    settings = Settings()
    print("\n   ✅ Settings создан успешно!")
    
    # Проверка атрибутов
    if hasattr(settings, 'telegram_bot_token'):
        print(f"   ✅ telegram_bot_token: {settings.telegram_bot_token[:20]}...")
    else:
        print("   ❌ telegram_bot_token: АТРИБУТ ОТСУТСТВУЕТ!")
        
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

print("\n" + "=" * 60)