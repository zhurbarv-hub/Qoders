import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'kkt_services.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== ПРОВЕРКА БАЗЫ ДАННЫХ ===\n")

# Клиенты
cursor.execute("SELECT COUNT(*) FROM clients")
print(f"Клиентов: {cursor.fetchone()[0]}")

# Сроки
cursor.execute("SELECT COUNT(*) FROM deadlines")
print(f"Сроков: {cursor.fetchone()[0]}")

# Типы сроков
cursor.execute("SELECT COUNT(*) FROM deadline_types")
print(f"Типов сроков: {cursor.fetchone()[0]}")

# Скоро истекающие
cursor.execute("SELECT COUNT(*) FROM v_expiring_soon")
print(f"Скоро истекает: {cursor.fetchone()[0]}")

print("\n✅ База данных работает!")

conn.close()