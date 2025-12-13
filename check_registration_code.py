from backend.database import SessionLocal
from backend.models import User
from datetime import datetime

db = SessionLocal()

# Найти всех пользователей с кодом регистрации
users_with_code = db.query(User).filter(User.registration_code != None).all()

print(f"\n=== Пользователи с кодом регистрации ===")
print(f"Всего найдено: {len(users_with_code)}\n")

for user in users_with_code:
    print(f"ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Компания: {user.company_name}")
    print(f"Роль: {user.role}")
    print(f"Код: {user.registration_code}")
    print(f"Код истекает: {user.code_expires_at}")
    if user.code_expires_at:
        is_expired = datetime.now() > user.code_expires_at
        print(f"Код истёк: {'ДА' if is_expired else 'НЕТ'}")
    print(f"Telegram ID: {user.telegram_id}")
    print(f"Telegram username: {user.telegram_username}")
    print(f"Активен: {user.is_active}")
    print("-" * 50)

db.close()
