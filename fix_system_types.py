import sqlite3

db_path = r"d:\QoProj\KKT\database\kkt_services.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔧 Исправление системных типов...")
print("=" * 80)

# Получить системные типы
cursor.execute("""
    SELECT id, type_name, is_system, is_active
    FROM deadline_types
    WHERE is_system = 1
""")

system_types = cursor.fetchall()

if not system_types:
    print("✅ Системных типов не найдено!")
else:
    print(f"Найдено {len(system_types)} системных типов:\n")
    
    for t in system_types:
        id, type_name, is_system, is_active = t
        print(f"ID {id}: {type_name}")
    
    print("\n" + "=" * 80)
    print("Меняю is_system=1 на is_system=0 (делаю пользовательскими)...")
    
    # Изменить все системные типы на пользовательские
    cursor.execute("""
        UPDATE deadline_types
        SET is_system = 0
        WHERE is_system = 1
    """)
    
    conn.commit()
    
    print(f"✅ Обновлено {cursor.rowcount} записей")
    
    # Проверка
    cursor.execute("""
        SELECT id, type_name, is_system, is_active
        FROM deadline_types
        ORDER BY id
    """)
    
    all_types = cursor.fetchall()
    
    print("\n" + "=" * 80)
    print("ТЕКУЩЕЕ СОСТОЯНИЕ ВСЕХ ТИПОВ:")
    print("=" * 80)
    
    for t in all_types:
        id, type_name, is_system, is_active = t
        system_flag = "🔧 Системный" if is_system else "👤 Пользовательский"
        active_flag = "✅ Активен" if is_active else "❌ Неактивен"
        print(f"\nID {id}: {type_name}")
        print(f"  {system_flag} | {active_flag}")

conn.close()

print("\n" + "=" * 80)
print("✅ ГОТОВО! Теперь все типы пользовательские и будут отображаться в списке.")
print("=" * 80)
