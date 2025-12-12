import sqlite3
import os

db_path = 'database/kkt_services.db'

if not os.path.exists(db_path):
    print(f"❌ База данных не найдена: {db_path}")
    exit(1)

print(f"✅ База данных найдена: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Получить список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

if not tables:
    print("❌ База данных пустая - нет таблиц!")
    print("\n🔧 Необходимо выполнить инициализацию:")
    print("   venv_web\\Scripts\\python database\\init_database.py")
else:
    print(f"\n📊 Таблицы в БД ({len(tables)}):")
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"   - {table_name}: {count} записей")

conn.close()
