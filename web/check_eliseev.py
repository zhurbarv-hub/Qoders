# -*- coding: utf-8 -*-
"""
Проверка пользователей с поиском по имени
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.database_url)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT username, email, full_name, role, 
               CASE WHEN password_hash IS NOT NULL THEN 'Yes' ELSE 'No' END as has_password
        FROM users 
        WHERE LOWER(username) LIKE '%elise%' OR LOWER(full_name) LIKE '%elise%'
    """))
    
    print("\n=== ПОИСК ПОЛЬЗОВАТЕЛЕЙ (Elise) ===\n")
    print(f"{'Username':<20} {'Email':<30} {'Полное имя':<30} {'Роль':<10} {'Пароль':<10}")
    print("-" * 110)
    
    found = False
    for row in result:
        found = True
        print(f"{row.username:<20} {row.email:<30} {row.full_name:<30} {row.role:<10} {row.has_password:<10}")
    
    if not found:
        print("Пользователи не найдены")
    
    print("\n" + "=" * 110 + "\n")
