# -*- coding: utf-8 -*-
"""
Инициализация базы данных KKT
Создаёт все таблицы и загружает начальные данные
"""

import sqlite3
import os
import sys

def init_database():
    """Создание и инициализация базы данных"""
    
    # Путь к базе данных
    db_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(db_dir, 'kkt_services.db')
    
    print("=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ KKT")
    print("=" * 60)
    print(f"\nПуть к БД: {db_path}\n")
    
    # Удаляем старую БД если существует
    if os.path.exists(db_path):
        response = input("⚠️  База данных уже существует. Пересоздать? (yes/no): ")
        if response.lower() != 'yes':
            print("Отменено.")
            return False
        os.remove(db_path)
        print("✓ Старая БД удалена")
    
    # Создаём подключение
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Выполняем схему
        schema_path = os.path.join(db_dir, 'schema_kkt.sql')
        print(f"\n📄 Выполнение: schema_kkt.sql")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
        print("✓ Схема создана")
        
        # Загружаем начальные данные
        seed_path = os.path.join(db_dir, 'seed_data.sql')
        print(f"\n📄 Выполнение: seed_data.sql")
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_sql = f.read()
            cursor.executescript(seed_sql)
        print("✓ Данные загружены")
        
        conn.commit()
        
        # Проверка
        print("\n" + "=" * 60)
        print("ПРОВЕРКА СОЗДАННЫХ ТАБЛИЦ")
        print("=" * 60)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("\nСозданные таблицы:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table[0]:<25} ({count} записей)")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        views = cursor.fetchall()
        
        print("\nСозданные представления:")
        for view in views:
            print(f"  ✓ {view[0]}")
        
        print("\n" + "=" * 60)
        print("✅ БАЗА ДАННЫХ УСПЕШНО СОЗДАНА!")
        print("=" * 60)
        print(f"\n📌 Путь к БД: {db_path}")
        print("\n📝 Данные для входа:")
        print("   Email: admin@kkt.local")
        print("   Password: admin123")
        print("   ⚠️  ВАЖНО: Смените пароль после первого входа!\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    try:
        success = init_database()
        if success:
            input("\nНажмите Enter для выхода...")
        else:
            input("\nОшибка! Нажмите Enter для выхода...")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)