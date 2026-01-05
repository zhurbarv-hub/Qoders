# -*- coding: utf-8 -*-
"""
Обновление пароля бота в PostgreSQL
"""
import psycopg2
import bcrypt

def get_password_hash(password: str) -> str:
    """Хеширование пароля через bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

conn = psycopg2.connect(
    "postgresql://kkt_user:KKT2024SecurePass@localhost:5432/kkt_production"
)
cur = conn.cursor()

# Поиск пользователя admin
cur.execute("SELECT id, email, role, password_hash FROM users WHERE email = %s", ('eliseev@relabs.center',))
admin_user = cur.fetchone()

if not admin_user:
    print("❌ Пользователь 'eliseev@relabs.center' не найден!")
    exit(1)

user_id, email, role, old_hash = admin_user
print(f"✅ Найден: {email} (ID={user_id}, Role={role})")

new_password = "admin123"

# Проверка текущего пароля
if old_hash and verify_password(new_password, old_hash):
    print(f"✅ Пароль уже установлен на '{new_password}'")
    exit(0)

# Генерация нового хеша
print(f"🔐 Генерация хеша для '{new_password}'...")
new_hash = get_password_hash(new_password)

# Обновление
cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
conn.commit()

print("✅ Пароль обновлён!")

# Проверка
cur.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
updated_hash = cur.fetchone()[0]

if verify_password(new_password, updated_hash):
    print("✅ Проверка пройдена!")
else:
    print("❌ Ошибка проверки!")

cur.close()
conn.close()
# -*- coding: utf-8 -*-
"""
Обновление пароля бота в PostgreSQL
"""
import psycopg2
import bcrypt

def get_password_hash(password: str) -> str:
    """Хеширование пароля через bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

conn = psycopg2.connect(
    "postgresql://kkt_user:KKT2024SecurePass@localhost:5432/kkt_production"
)
cur = conn.cursor()

# Поиск пользователя admin
cur.execute("SELECT id, email, role, password_hash FROM users WHERE email = %s", ('eliseev@relabs.center',))
admin_user = cur.fetchone()

if not admin_user:
    print("❌ Пользователь 'eliseev@relabs.center' не найден!")
    exit(1)

user_id, email, role, old_hash = admin_user
print(f"✅ Найден: {email} (ID={user_id}, Role={role})")

new_password = "admin123"

# Проверка текущего пароля
if old_hash and verify_password(new_password, old_hash):
    print(f"✅ Пароль уже установлен на '{new_password}'")
    exit(0)

# Генерация нового хеша
print(f"🔐 Генерация хеша для '{new_password}'...")
new_hash = get_password_hash(new_password)

# Обновление
cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user_id))
conn.commit()

print("✅ Пароль обновлён!")

# Проверка
cur.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
updated_hash = cur.fetchone()[0]

if verify_password(new_password, updated_hash):
    print("✅ Проверка пройдена!")
else:
    print("❌ Ошибка проверки!")

cur.close()
conn.close()
