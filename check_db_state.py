#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка состояния базы данных - клиенты и дедлайны
"""
import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

from web.app.database import SessionLocal
from web.app.models.user import User
from web.app.models.client import Deadline
from sqlalchemy import and_

db = SessionLocal()

print("=" * 60)
print("ПРОВЕРКА СОСТОЯНИЯ БАЗЫ ДАННЫХ")
print("=" * 60)

# Проверяем клиентов
active_clients = db.query(User).filter(User.role == 'client', User.is_active == True).count()
all_clients = db.query(User).filter(User.role == 'client').count()
inactive_clients = all_clients - active_clients

print(f"\n📊 КЛИЕНТЫ:")
print(f"   Активных: {active_clients}")
print(f"   Неактивных: {inactive_clients}")
print(f"   Всего: {all_clients}")

# Проверяем дедлайны
all_deadlines = db.query(Deadline).count()
active_deadlines = db.query(Deadline).filter(Deadline.status == 'active').count()

print(f"\n📅 ДЕДЛАЙНЫ:")
print(f"   Всего в БД: {all_deadlines}")
print(f"   Со статусом 'active': {active_deadlines}")

# Проверяем дедлайны у неактивных клиентов
deadlines_of_inactive = db.query(Deadline).join(
    User, Deadline.client_id == User.id
).filter(User.is_active == False).count()

print(f"   У неактивных клиентов: {deadlines_of_inactive}")

# Показать примеры дедлайнов
print(f"\n🔍 ПРИМЕРЫ ДЕДЛАЙНОВ (первые 10):")
deadlines_sample = db.query(Deadline).limit(10).all()

for d in deadlines_sample:
    client = db.query(User).filter(User.id == d.client_id).first()
    client_name = client.full_name if client else "КЛИЕНТ НЕ НАЙДЕН"
    client_active = "✅" if (client and client.is_active) else "❌"
    print(f"   ID={d.id:3d} | client_id={d.client_id:3d} {client_active} | {client_name[:30]:30s} | status={d.status}")

# Проверяем "осиротевшие" дедлайны
orphaned = db.query(Deadline).filter(
    ~Deadline.client_id.in_(db.query(User.id).filter(User.role == 'client'))
).count()

print(f"\n⚠️  ОСИРОТЕВШИЕ ДЕДЛАЙНЫ (client_id не существует): {orphaned}")

db.close()
print("\n" + "=" * 60)
