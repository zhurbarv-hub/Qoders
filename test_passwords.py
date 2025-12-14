#!/usr/bin/env python3
"""
Тестирование различных паролей для Eliseev
"""
import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

from web.app.models.user import User
from web.app.services.auth_service import verify_password
from web.app.database import SessionLocal

db = SessionLocal()

try:
    user = db.query(User).filter(User.username == "Eliseev").first()
    
    if user and user.password_hash:
        print(f"Тестирование паролей для пользователя: {user.username}")
        print(f"Password Hash: {user.password_hash[:60]}...\n")
        
        # Список возможных паролей
        passwords_to_test = [
            "7ywyrfrwei-",
            "Qwerty123",
            "qwerty123",
            "admin123",
            "Admin123",
            "eliseev",
            "Eliseev",
            "eliseev123",
            "Eliseev123",
            "7ywyrfrwei",
            "password",
            "Password123"
        ]
        
        print("Проверка паролей:")
        for pwd in passwords_to_test:
            is_valid = verify_password(pwd, user.password_hash)
            status = "✅ СОВПАДАЕТ!" if is_valid else "❌"
            print(f"  {status} '{pwd}'")
            if is_valid:
                print(f"\n🎉 НАЙДЕН ПРАВИЛЬНЫЙ ПАРОЛЬ: '{pwd}'")
                break
    else:
        print("Пользователь не найден или пароль не установлен")
        
finally:
    db.close()
