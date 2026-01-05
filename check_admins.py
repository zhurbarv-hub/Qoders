#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка пользователей админов"""

import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'kkt_production',
    'user': 'kkt_user',
    'password': 'KKT2024SecurePass'
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT username, full_name, role 
        FROM users 
        WHERE role IN ('admin', 'manager')
        ORDER BY username
    """)
    
    print("Администраторы и менеджеры:")
    for row in cursor.fetchall():
        username, full_name, role = row
        print(f"  {username} ({full_name}) - роль: {role}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Ошибка: {e}")
