#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест восстановления БД
"""
import sys
import time
sys.path.insert(0, '/home/kktapp/kkt-system')

from web.app.database import SessionLocal
from web.app.models.user import User

print("=" * 60)
print("ТЕСТ ВОССТАНОВЛЕНИЯ БАЗЫ ДАННЫХ")
print("=" * 60)

# Состояние ДО
db = SessionLocal()
print("\n📊 СОСТОЯНИЕ ДО:")
before_count = db.query(User).count()
before_active = db.query(User).filter(User.is_active == True).count()
print(f"  Всего пользователей: {before_count}")
print(f"  Активных: {before_active}")
db.close()

# Тест восстановления
print("\n🔄 ЗАПУСК ВОССТАНОВЛЕНИЯ...")
print("  (это займёт 3-5 секунд)")

import subprocess
import os
from pathlib import Path

BACKUP_FILE = "/home/kktapp/kkt-system/backups/database/kkt_backup_20251220_085222.sql"

if not Path(BACKUP_FILE).exists():
    print(f"❌ Файл бэкапа не найден: {BACKUP_FILE}")
    sys.exit(1)

env = os.environ.copy()
env['PGPASSWORD'] = 'KKT2024SecurePass'

cmd = [
    'psql',
    '-h', 'localhost',
    '-p', '5432',
    '-U', 'kkt_user',
    '-d', 'kkt_production',
    '-f', BACKUP_FILE,
    '--single-transaction',
    '--set', 'ON_ERROR_STOP=on',
    '-v', 'ON_ERROR_STOP=1',
    '-q'
]

start_time = time.time()

result = subprocess.run(
    cmd,
    env=env,
    capture_output=True,
    text=True
)

elapsed = time.time() - start_time

if result.returncode == 0:
    print(f"✅ Восстановление завершено за {elapsed:.2f} сек")
else:
    print(f"❌ Ошибка восстановления:")
    print(result.stderr)
    sys.exit(1)

# Состояние ПОСЛЕ
time.sleep(1)
db = SessionLocal()
print("\n📊 СОСТОЯНИЕ ПОСЛЕ:")
after_count = db.query(User).count()
after_active = db.query(User).filter(User.is_active == True).count()
print(f"  Всего пользователей: {after_count}")
print(f"  Активных: {after_active}")
db.close()

print("\n" + "=" * 60)
print(f"РЕЗУЛЬТАТ: {'✅ УСПЕХ' if after_count > 0 else '❌ ПРОБЛЕМА'}")
print(f"Время выполнения: {elapsed:.2f} сек")
print("=" * 60)
