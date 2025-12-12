"""
Проверка пользователей в базе данных
"""
import sqlite3

db_path = r"d:\QoProj\KKT\database\kkt_services.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ В БД")
print("=" * 60)

# Проверяем таблицу web_users
cursor.execute("SELECT id, username, email, role, is_active FROM web_users")
users = cursor.fetchall()

print(f"\nНайдено пользователей: {len(users)}")
print("\nСписок пользователей:")
print("-" * 60)

for user in users:
    user_id, username, email, role, is_active = user
    status = "Активен" if is_active else "Неактивен"
    print(f"ID: {user_id}")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Role: {role}")
    print(f"Status: {status}")
    print("-" * 60)

conn.close()

print("\nДля входа используйте:")
print("Username: <username из списка>")
print("Password: <пароль, который вы устанавливали>")
