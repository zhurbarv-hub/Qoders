# -*- coding: utf-8 -*-
"""Проверка пользователей с ролью admin/manager"""
import sqlite3

conn = sqlite3.connect('database/kkt_services.db')
cursor = conn.cursor()

print("=" * 70)
print("ПОЛЬЗОВАТЕЛИ С РОЛЯМИ ADMIN/MANAGER")
print("=" * 70)

cursor.execute('''
    SELECT id, email, role, is_active, full_name 
    FROM users 
    WHERE role IN ('admin', 'manager')
    ORDER BY id
''')

rows = cursor.fetchall()

if rows:
    print(f"\nНайдено: {len(rows)} пользователей\n")
    print(f"{'ID':<5} {'Email':<30} {'Role':<10} {'Active':<8} {'Full Name':<20}")
    print("-" * 70)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<30} {row[2]:<10} {row[3]:<8} {row[4] or 'N/A':<20}")
else:
    print("\n❌ Пользователи с ролями admin/manager не найдены!")

conn.close()
# -*- coding: utf-8 -*-
"""Проверка пользователей с ролью admin/manager"""
import sqlite3

conn = sqlite3.connect('database/kkt_services.db')
cursor = conn.cursor()

print("=" * 70)
print("ПОЛЬЗОВАТЕЛИ С РОЛЯМИ ADMIN/MANAGER")
print("=" * 70)

cursor.execute('''
    SELECT id, email, role, is_active, full_name 
    FROM users 
    WHERE role IN ('admin', 'manager')
    ORDER BY id
''')

rows = cursor.fetchall()

if rows:
    print(f"\nНайдено: {len(rows)} пользователей\n")
    print(f"{'ID':<5} {'Email':<30} {'Role':<10} {'Active':<8} {'Full Name':<20}")
    print("-" * 70)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<30} {row[2]:<10} {row[3]:<8} {row[4] or 'N/A':<20}")
else:
    print("\n❌ Пользователи с ролями admin/manager не найдены!")

conn.close()
