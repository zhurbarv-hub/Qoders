#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт применения миграции 011 - добавление last_login в таблицу users
"""

import psycopg2
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
    """Применить миграцию 011"""
    migration_file = Path(__file__).parent / 'app' / 'migrations' / '011_add_last_login_to_users.sql'
    
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
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'last_login';
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Колонка создана успешно:")
            print(f"   - Имя: {result[0]}")
            print(f"   - Тип: {result[1]}")
            print(f"   - Nullable: {result[2]}")
        else:
            print("❌ Колонка не найдена!")
            conn.rollback()
            return False
        
        conn.commit()
        print("\n✅ Миграция 011 применена успешно!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при применении миграции: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  ПРИМЕНЕНИЕ МИГРАЦИИ 011: ADD LAST_LOGIN TO USERS")
    print("=" * 60)
    print()
    
    success = apply_migration()
    
    if success:
        print("\n🎉 Готово! Теперь можно перезапустить веб-сервис.")
    else:
        print("\n❌ Миграция не применена. Проверьте ошибки выше.")
