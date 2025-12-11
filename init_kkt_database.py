# -*- coding: utf-8 -*-
"""
Инициализация базы данных KKT с правильной схемой
"""
import sqlite3
import os

# Путь к базе данных
DB_PATH = "kkt_system.db"
SCHEMA_PATH = "database/schema_kkt.sql"

def init_database():
    """Инициализация базы данных"""
    print("=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ KKT")
    print("=" * 60)
    
    # Проверка существования схемы
    if not os.path.exists(SCHEMA_PATH):
        print(f"❌ Файл схемы не найден: {SCHEMA_PATH}")
        return False
    
    # Чтение SQL схемы
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    try:
        # Подключение к БД
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"\n📁 База данных: {os.path.abspath(DB_PATH)}")
        print(f"📄 Схема: {SCHEMA_PATH}")
        
        # Выполнение SQL схемы
        print("\n🔄 Создание таблиц...")
        cursor.executescript(schema_sql)
        conn.commit()
        
        # Проверка созданных таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n✅ Таблицы созданы успешно ({len(tables)}):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  • {table[0]:<30} ({count} записей)")
        
        conn.close()
        
        print("\n✅ База данных успешно инициализирована!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    init_database()