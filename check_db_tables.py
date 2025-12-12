import sqlite3

db_path = "database/kkt_services.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("ТАБЛИЦЫ В БАЗЕ ДАННЫХ")
    print("=" * 60)
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    
    tables = cursor.fetchall()
    
    if not tables:
        print("❌ Таблицы не найдены!")
    else:
        print(f"\nВсего таблиц: {len(tables)}\n")
        
        for idx, (table_name,) in enumerate(tables, 1):
            print(f"{idx}. {table_name}")
            
            # Показываем структуру каждой таблицы
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            if columns:
                print(f"   Колонки:")
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    pk_mark = " (PK)" if pk else ""
                    not_null_mark = " NOT NULL" if not_null else ""
                    print(f"     - {col_name}: {col_type}{not_null_mark}{pk_mark}")
            
            # Показываем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Записей: {count}\n")
    
    print("=" * 60)
    
    conn.close()
    
except Exception as e:
    print(f"❌ Ошибка при работе с БД: {e}")
