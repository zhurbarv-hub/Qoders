#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка дедлайнов и касс"""

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
    
    print("=" * 60)
    print("ДЕДЛАЙНЫ ПО КАССАМ")
    print("=" * 60)
    
    cursor.execute("""
        SELECT 
            d.id as deadline_id,
            d.status as deadline_status,
            d.cash_register_id,
            cr.model as register_model,
            cr.is_active as register_active,
            u.company_name as client_name,
            u.is_active as client_active
        FROM deadlines d
        LEFT JOIN cash_registers cr ON d.cash_register_id = cr.id
        LEFT JOIN users u ON d.client_id = u.id
        WHERE d.cash_register_id IS NOT NULL
        ORDER BY d.id
    """)
    
    rows = cursor.fetchall()
    print(f"Найдено {len(rows)} дедлайнов по кассам:\n")
    
    active_with_active_register = 0
    active_with_inactive_register = 0
    cancelled_deadlines = 0
    
    for row in rows:
        dl_id, dl_status, reg_id, reg_model, reg_active, client, client_active = row
        
        if dl_status == 'cancelled':
            cancelled_deadlines += 1
            status_icon = "🚫"
        elif dl_status == 'active' and reg_active:
            active_with_active_register += 1
            status_icon = "✅"
        elif dl_status == 'active' and not reg_active:
            active_with_inactive_register += 1
            status_icon = "❌"
        else:
            status_icon = "❓"
        
        print(f"{status_icon} Дедлайн ID={dl_id} | Статус={dl_status}")
        print(f"   Касса #{reg_id}: {reg_model} | Активна: {reg_active}")
        print(f"   Клиент: {client} | Активен: {client_active}")
        print()
    
    print("=" * 60)
    print("ИТОГО:")
    print(f"  ✅ Активных дедлайнов с активными кассами: {active_with_active_register}")
    print(f"  ❌ Активных дедлайнов с неактивными кассами: {active_with_inactive_register}")
    print(f"  🚫 Отменённых дедлайнов: {cancelled_deadlines}")
    print("=" * 60)
    
    if active_with_inactive_register > 0:
        print(f"\n⚠️  ПРОБЛЕМА: {active_with_inactive_register} активных дедлайнов привязаны к неактивным кассам!")
    else:
        print("\n✅ Всё в порядке: нет активных дедлайнов с неактивными кассами")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Ошибка: {e}")
