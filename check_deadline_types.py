import sqlite3
import os

# Путь к базе данных
db_path = r"d:\QoProj\KKT\database\kkt_services.db"

if not os.path.exists(db_path):
    print(f"❌ База данных не найдена: {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Получить все типы дедлайнов
    cursor.execute("""
        SELECT id, type_name, description, is_system, is_active, created_at
        FROM deadline_types
        ORDER BY id
    """)
    
    types = cursor.fetchall()
    
    print("=" * 80)
    print("ВСЕ ТИПЫ ДЕДЛАЙНОВ В БАЗЕ ДАННЫХ")
    print("=" * 80)
    
    for t in types:
        id, type_name, description, is_system, is_active, created_at = t
        status = []
        if is_system:
            status.append("🔧 СИСТЕМНЫЙ")
        if not is_active:
            status.append("❌ НЕАКТИВЕН")
        if not status:
            status.append("✅ Активен")
        
        print(f"\nID: {id}")
        print(f"Название: {type_name}")
        print(f"Описание: {description or '-'}")
        print(f"Статус: {' | '.join(status)}")
        print(f"Создан: {created_at}")
    
    print("\n" + "=" * 80)
    print(f"Всего типов: {len(types)}")
    
    # Проверить конкретно "Замена ФН"
    cursor.execute("""
        SELECT id, type_name, description, is_system, is_active
        FROM deadline_types
        WHERE type_name LIKE '%ФН%' OR type_name LIKE '%фн%'
    """)
    
    fn_types = cursor.fetchall()
    if fn_types:
        print("\n" + "=" * 80)
        print("НАЙДЕНЫ ТИПЫ СО СЛОВОМ 'ФН':")
        print("=" * 80)
        for t in fn_types:
            id, type_name, description, is_system, is_active = t
            print(f"\nID: {id} | {type_name}")
            print(f"  Системный: {is_system} | Активен: {is_active}")
            
            if is_system:
                print(f"\n🔧 Это СИСТЕМНЫЙ тип - нужно сделать пользовательским!")
                print(f"   Выполните: UPDATE deadline_types SET is_system=0 WHERE id={id};")
            
            if not is_active:
                print(f"\n❌ Тип НЕАКТИВЕН - нужно активировать!")
                print(f"   Выполните: UPDATE deadline_types SET is_active=1 WHERE id={id};")
    
    conn.close()
