# -*- coding: utf-8 -*-
"""
Скрипт для проверки username в таблице users
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from sqlalchemy import create_engine, text
from app.config import settings

# Подключение к БД
engine = create_engine(settings.database_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, username, email, full_name, role FROM users ORDER BY id"))
    
    print("\n=== ПОЛЬЗОВАТЕЛИ В СИСТЕМЕ ===\n")
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Полное имя':<30} {'Роль':<10}")
    print("-" * 100)
    
    for row in result:
        print(f"{row.id:<5} {row.username:<20} {row.email:<30} {row.full_name:<30} {row.role:<10}")
    
    print("\n" + "=" * 100 + "\n")
