#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка дубликатов Telegram ID"""

import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

from web.app.database import SessionLocal
from web.app.models.user import User

db = SessionLocal()

telegram_id = '556319278'
users = db.query(User).filter(User.telegram_id == telegram_id).all()

print(f'Users with telegram_id {telegram_id}:')
for u in users:
    print(f'  ID: {u.id}, Username: {u.username}, Role: {u.role}, Full Name: {u.full_name}')

db.close()
