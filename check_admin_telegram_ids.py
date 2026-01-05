#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка Telegram ID администраторов"""

import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

from web.app.database import SessionLocal
from web.app.models.user import User

db = SessionLocal()

# Получаем всех администраторов
admins = db.query(User).filter(User.role == 'admin').all()

print("=" * 60)
print("АДМИНИСТРАТОРЫ СИСТЕМЫ:")
print("=" * 60)

for admin in admins:
    print(f"\nID: {admin.id}")
    print(f"Логин: {admin.username}")
    print(f"ФИО: {admin.full_name}")
    print(f"Email: {admin.email}")
    print(f"Telegram ID: {admin.telegram_id or 'НЕ УКАЗАН'}")
    print(f"Активен: {admin.is_active}")
    print("-" * 60)

# Собираем все Telegram ID для .env
telegram_ids = [str(admin.telegram_id) for admin in admins if admin.telegram_id and admin.is_active]

print("\n" + "=" * 60)
print("СПИСОК ДЛЯ .env (ADMIN_TELEGRAM_IDS):")
print("=" * 60)
print(",".join(telegram_ids))
print()

db.close()
