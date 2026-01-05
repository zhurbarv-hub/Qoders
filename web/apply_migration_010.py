#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт применения миграции 010 на VDS
Добавляет поля register_name и installation_address в таблицу cash_registers
"""

import psycopg2
import os
from pathlib import Path

# Параметры подключения к VDS
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'kkt_db',
    'user': 'kkt_user',
    'password': 'kkt_secure_password_2024'
}

def apply_migration():
    """Применить миграцию 010"""
    migration_file = Path(__file__).parent / 'app' / 'migrations' / '010_add_cash_register_name_and_address.sql'
    
    if not migration_file.exists():
        print(f"❌ Файл миграции не найден: {migration_file}")
        return False
    
    print("📋 Чтение SQL-миграции...")
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print(f"📄 Содержимое миграции:\n{migration_sql}\n")
    
    try:
        print("🔌 Подключение к базе данных...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("⚙️  Применение миграции...")
        cursor.execute(migration_sql)
        
        print("✅ Проверка результата...")
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'cash_registers' 
            AND column_name IN ('register_name', 'installation_address')
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        if columns:
            print("\n✅ Добавленные столбцы:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}" + (f"({col[2]})" if col[2] else ""))
        else:
            print("⚠️  Столбцы не найдены!")
            conn.rollback()
            return False
        
        conn.commit()
        print("\n✅ Миграция успешно применена!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при применении миграции: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Применение миграции 010: register_name и installation_address")
    print("=" * 60)
    success = apply_migration()
    print("=" * 60)
    exit(0 if success else 1)
