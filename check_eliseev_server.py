#!/usr/bin/env python3
"""
Проверка пользователя Eliseev на сервере
"""
import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

from web.app.models.user import User
from web.app.database import SessionLocal

db = SessionLocal()

try:
    user = db.query(User).filter(User.username == "Eliseev").first()
    
    if user:
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Is Active: {user.is_active}")
        print(f"Has Password: {'Yes' if user.password_hash else 'No'}")
        if user.password_hash:
            print(f"Password Hash: {user.password_hash[:50]}...")
    else:
        print("User Eliseev not found")
        
finally:
    db.close()
