# -*- coding: utf-8 -*-
"""
Проверка наличия необходимых типов дедлайнов для автоматизации
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "kkt_services.db"

def check_deadline_types():
    """Проверить наличие типов 'Замена ФН' и 'Продление договора'"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔍 Поиск необходимых типов дедлайнов...")
    print()
    
    # Поиск типа "Замена ФН"
    cursor.execute("""
        SELECT id, type_name, description, is_system, is_active
        FROM deadline_types
        WHERE type_name LIKE '%замен%ФН%' OR type_name LIKE '%замен%фн%'
        COLLATE NOCASE
    """)
    fn_types = cursor.fetchall()
    
    print("📋 Типы для замены ФН:")
    if fn_types:
        for t in fn_types:
            print(f"   ✓ ID:{t[0]} | {t[1]} | Активен:{t[4]}")
    else:
        print("   ❌ Не найдено!")
        print("   Необходимо создать тип 'Замена ФН'")
    print()
    
    # Поиск типа "Продление договора" или связанного с ОФД
    cursor.execute("""
        SELECT id, type_name, description, is_system, is_active
        FROM deadline_types
        WHERE (type_name LIKE '%продлен%' OR type_name LIKE '%ОФД%' OR type_name LIKE '%офд%')
        COLLATE NOCASE
    """)
    ofd_types = cursor.fetchall()
    
    print("📋 Типы для продления ОФД:")
    if ofd_types:
        for t in ofd_types:
            print(f"   ✓ ID:{t[0]} | {t[1]} | Активен:{t[4]}")
    else:
        print("   ❌ Не найдено!")
        print("   Необходимо создать тип 'Продление договора'")
    print()
    
    # Показать все типы
    cursor.execute("SELECT id, type_name, is_active FROM deadline_types")
    all_types = cursor.fetchall()
    
    print("📋 Все типы дедлайнов в системе:")
    for t in all_types:
        status = "✓" if t[2] else "✗"
        print(f"   {status} ID:{t[0]} | {t[1]}")
    print()
    
    conn.close()
    
    return bool(fn_types), bool(ofd_types)

def create_missing_types():
    """Создать отсутствующие типы дедлайнов"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("➕ Создание отсутствующих типов дедлайнов...")
    print()
    
    try:
        # Проверка и создание типа "Замена ФН"
        cursor.execute("""
            SELECT COUNT(*) FROM deadline_types
            WHERE type_name = 'Замена ФН'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO deadline_types (type_name, description, is_system, is_active)
                VALUES ('Замена ФН', 'Замена фискального накопителя', 0, 1)
            """)
            print("   ✓ Создан тип 'Замена ФН'")
        else:
            print("   ⏭️  Тип 'Замена ФН' уже существует")
        
        # Проверка и создание типа "Продление договора"
        cursor.execute("""
            SELECT COUNT(*) FROM deadline_types
            WHERE type_name = 'Продление договора'
        """)
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO deadline_types (type_name, description, is_system, is_active)
                VALUES ('Продление договора', 'Продление договора с ОФД', 0, 1)
            """)
            print("   ✓ Создан тип 'Продление договора'")
        else:
            print("   ⏭️  Тип 'Продление договора' уже существует")
        
        conn.commit()
        print()
        print("✅ Типы дедлайнов готовы к использованию")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка SQLite: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 80)
    print("ПРОВЕРКА ТИПОВ ДЕДЛАЙНОВ ДЛЯ АВТОМАТИЗАЦИИ")
    print("=" * 80)
    print()
    
    has_fn, has_ofd = check_deadline_types()
    
    if not has_fn or not has_ofd:
        print("⚠️  Требуется создание отсутствующих типов")
        print()
        create_missing_types()
    else:
        print("✅ Все необходимые типы дедлайнов найдены")
    
    print()
    print("=" * 80)
