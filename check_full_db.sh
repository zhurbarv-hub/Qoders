#!/bin/bash
# Проверка БД
cd /home/kktapp/kkt-system
source venv/bin/activate

echo "=== ПРОВЕРКА БАЗЫ ДАННЫХ ==="
python3 << 'PYEOF'
from web.app.database import SessionLocal
from web.app.models.user import User
from web.app.models.client import Deadline
from web.app.models.cash_register import CashRegister

db = SessionLocal()

print("\n📊 ПОЛЬЗОВАТЕЛИ:")
print(f"  Всего: {db.query(User).count()}")
print(f"  Клиентов (всего): {db.query(User).filter(User.role=='client').count()}")
print(f"  Клиентов (активных): {db.query(User).filter(User.role=='client', User.is_active==True).count()}")
print(f"  Админов: {db.query(User).filter(User.role=='admin').count()}")

print("\n📅 ДЕДЛАЙНЫ:")
print(f"  Всего: {db.query(Deadline).count()}")
print(f"  Активных: {db.query(Deadline).filter(Deadline.status=='active').count()}")

print("\n💰 КАССЫ:")
print(f"  Всего: {db.query(CashRegister).count()}")
print(f"  Активных: {db.query(CashRegister).filter(CashRegister.is_active==True).count()}")

# Примеры данных
print("\n👥 ПРИМЕРЫ ПОЛЬЗОВАТЕЛЕЙ:")
users = db.query(User).limit(5).all()
for u in users:
    print(f"  ID={u.id}, role={u.role}, active={u.is_active}, name={u.full_name}")

db.close()
PYEOF
