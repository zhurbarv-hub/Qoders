"""
Проверка, есть ли вы в таблице Contact
"""
from backend.database import SessionLocal
from backend.models import Contact
from backend.config import settings

db = SessionLocal()

print("=" * 60)
print("ПРОВЕРКА ТАБЛИЦЫ КОНТАКТОВ")
print("=" * 60)

your_id = input("Ваш Telegram ID: ")

contact = db.query(Contact).filter(
    Contact.telegram_id == your_id
).first()

if contact:
    print(f"\n✅ Вы найдены в таблице Contact!")
    print(f"   Client ID: {contact.client_id}")
    print(f"   Имя: {contact.name}")
    print(f"   Уведомления: {'✅' if contact.notifications_enabled else '❌'}")
else:
    print(f"\n❌ Вы НЕ найдены в таблице Contact")
    print(f"   Это нормально для администратора")

print(f"\n📋 TELEGRAM_ADMIN_ID из .env: {settings.telegram_admin_id}")
print(f"   Совпадает: {'✅' if str(settings.telegram_admin_id) == your_id else '❌'}")

db.close()
print("=" * 60)