#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавление ОФД провайдера "Контур НТТ"
"""

import psycopg2

# Параметры подключения к VDS
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'kkt_production',
    'user': 'kkt_user',
    'password': 'KKT2024SecurePass'
}

def add_kontur_ntt():
    """Добавить ОФД провайдера Контур НТТ"""
    
    try:
        print("🔌 Подключение к базе данных...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Сначала проверим структуру таблицы
        print("📋 Проверка структуры таблицы ofd_providers...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'ofd_providers'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("Колонки таблицы:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Проверим, есть ли уже такой провайдер
        print("\n🔍 Проверка существования провайдера...")
        cursor.execute("""
            SELECT id, name FROM ofd_providers 
            WHERE name LIKE '%Контур%НТТ%' OR name = 'Контур НТТ';
        """)
        
        existing = cursor.fetchone()
        if existing:
            print(f"⚠️  Провайдер уже существует: {existing}")
            conn.close()
            return True
        
        # Добавляем нового провайдера
        print("\n➕ Добавление провайдера 'Контур НТТ'...")
        cursor.execute("""
            INSERT INTO ofd_providers (name, website, support_phone, is_active) 
            VALUES (%s, %s, %s, %s)
            RETURNING id, name;
        """, ('Контур НТТ', 'https://ntt.kontur.ru', '8-800-100-49-13', True))
        
        result = cursor.fetchone()
        print(f"✅ Провайдер добавлен успешно: ID={result[0]}, Name={result[1]}")
        
        conn.commit()
        
        # Выведем список всех провайдеров
        print("\n📋 Список всех ОФД провайдеров:")
        cursor.execute("SELECT id, name, is_active FROM ofd_providers ORDER BY id;")
        providers = cursor.fetchall()
        for p in providers:
            status = "✅" if p[2] else "❌"
            print(f"  {status} [{p[0]}] {p[1]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  ДОБАВЛЕНИЕ ОФД ПРОВАЙДЕРА: КОНТУР НТТ")
    print("=" * 60)
    print()
    
    success = add_kontur_ntt()
    
    if success:
        print("\n🎉 Готово!")
    else:
        print("\n❌ Операция не выполнена.")
