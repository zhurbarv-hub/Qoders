#!/usr/bin/env python3
"""
Тестирование аутентификации пользователя Eliseev
"""
import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

from web.app.models.user import User
from web.app.services.auth_service import authenticate_user, verify_password
from web.app.database import SessionLocal

db = SessionLocal()

try:
    # Найти пользователя
    user = db.query(User).filter(User.username == "Eliseev").first()
    
    if user:
        print(f"✅ Пользователь найден:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Has Password: {'Да' if user.password_hash else 'Нет'}")
        
        if user.password_hash:
            print(f"   Password Hash (first 60 chars): {user.password_hash[:60]}...")
            
            # Тест аутентификации
            test_password = "7ywyrfrwei-"
            print(f"\n🔐 Тестирование аутентификации с паролем: '{test_password}'")
            
            # Прямая проверка пароля
            is_valid = verify_password(test_password, user.password_hash)
            print(f"   Прямая проверка пароля: {'✅ УСПЕШНО' if is_valid else '❌ НЕВЕРНО'}")
            
            # Через authenticate_user
            auth_user = authenticate_user(db, "Eliseev", test_password)
            print(f"   authenticate_user с username: {'✅ УСПЕШНО' if auth_user else '❌ НЕВЕРНО'}")
            
            # Через email
            auth_user_email = authenticate_user(db, user.email, test_password)
            print(f"   authenticate_user с email: {'✅ УСПЕШНО' if auth_user_email else '❌ НЕВЕРНО'}")
            
    else:
        print("❌ Пользователь 'Eliseev' не найден")
        
        # Показать всех пользователей
        all_users = db.query(User).all()
        print(f"\n📋 Всего пользователей: {len(all_users)}")
        for u in all_users[:10]:  # Первые 10
            print(f"   - {u.username} ({u.email}) - {u.role} - Active: {u.is_active}")
        
finally:
    db.close()
