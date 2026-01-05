#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Очистка дедлайнов у неактивных клиентов
"""
import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

from web.app.database import SessionLocal
from web.app.models.user import User
from web.app.models.client import Deadline

db = SessionLocal()

print("=" * 60)
print("ОЧИСТКА ДЕДЛАЙНОВ У НЕАКТИВНЫХ КЛИЕНТОВ")
print("=" * 60)

# Найти всех неактивных клиентов
inactive_clients = db.query(User).filter(
    User.role == 'client',
    User.is_active == False
).all()

print(f"\nНайдено неактивных клиентов: {len(inactive_clients)}")

total_deleted = 0

for client in inactive_clients:
    # Найти все дедлайны этого клиента
    deadlines = db.query(Deadline).filter(
        Deadline.client_id == client.id
    ).all()
    
    count = len(deadlines)
    if count > 0:
        print(f"\n  Клиент ID={client.id} '{client.full_name}':")
        print(f"    Найдено дедлайнов: {count}")
        
        # Удалить все дедлайны
        for deadline in deadlines:
            db.delete(deadline)
            print(f"      ✓ Удален дедлайн ID={deadline.id}")
        
        total_deleted += count

# Сохранить изменения
db.commit()

print(f"\n{'=' * 60}")
print(f"ИТОГО УДАЛЕНО: {total_deleted} дедлайнов")
print(f"{'=' * 60}")

# Проверка результата
remaining = db.query(Deadline).join(
    User, Deadline.client_id == User.id
).filter(User.is_active == False).count()

print(f"\nПроверка: осталось дедлайнов у неактивных клиентов: {remaining}")

db.close()
