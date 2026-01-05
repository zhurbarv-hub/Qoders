#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка количества активных касс у активных клиентов"""

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
    
    # Все активные кассы
    cursor.execute("SELECT COUNT(*) FROM cash_registers WHERE is_active = true")
    all_active = cursor.fetchone()[0]
    print(f"Всего активных касс: {all_active}")
    
    # Активные кассы у активных клиентов
    cursor.execute("""
        SELECT COUNT(*) 
        FROM cash_registers cr 
        JOIN users u ON cr.client_id = u.id 
        WHERE cr.is_active = true 
        AND u.is_active = true 
        AND u.role = 'client'
    """)
    active_client_registers = cursor.fetchone()[0]
    print(f"Активных касс у активных клиентов: {active_client_registers}")
    
    # Детали
    cursor.execute("""
        SELECT u.company_name, u.is_active as client_active, 
               COUNT(*) as registers_count
        FROM cash_registers cr 
        JOIN users u ON cr.client_id = u.id 
        WHERE cr.is_active = true
        GROUP BY u.id, u.company_name, u.is_active
        ORDER BY u.company_name
    """)
    
    print("\nДетали по клиентам:")
    for row in cursor.fetchall():
        company, is_active, count = row
        status = "✓ активен" if is_active else "✗ неактивен"
        print(f"  {company}: {count} касс(а) - {status}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Ошибка: {e}")
