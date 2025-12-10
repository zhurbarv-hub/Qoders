"""
Проверка настройки администратора
"""
from backend.config import settings

print("=" * 60)
print("ПРОВЕРКА НАСТРОЕК АДМИНИСТРАТОРА")
print("=" * 60)

print(f"\n📋 Из .env файла:")
print(f"   TELEGRAM_ADMIN_ID = {settings.telegram_admin_id}")
print(f"   Тип: {type(settings.telegram_admin_id)}")

print(f"\n💡 Ваш ID для проверки:")
your_id = input("   Введите ваш Telegram ID из @userinfobot: ")

if your_id.strip() == str(settings.telegram_admin_id):
    print("\n✅ ID СОВПАДАЕТ! Перезапустите бота.")
else:
    print(f"\n❌ ID НЕ СОВПАДАЕТ!")
    print(f"   В .env: {settings.telegram_admin_id}")
    print(f"   Ваш ID: {your_id}")
    print(f"\n🔧 Исправьте в .env и перезапустите бота")

print("=" * 60)