# -*- coding: utf-8 -*-
"""
Обновление пароля администратора
"""
import sqlite3
import os

# Путь к базе данных
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "kkt_system.db")

# Новый хеш пароля
NEW_PASSWORD_HASH = "$2b$12$A3ahw.Bglc/nsIJhCUSaSewmOhw/vACfPYu73UkEQDSzZ89Ayei4u"

def update_password():
    """Обновить пароль администратора"""
    print(f"📁 База данных: {DATABASE_PATH}")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Обновление пароля
        cursor.execute(
            "UPDATE web_users SET password_hash = ? WHERE username = ?",
            (NEW_PASSWORD_HASH, 'admin')
        )
        conn.commit()
        
        # Проверка
        cursor.execute(
            "SELECT username, email, role FROM web_users WHERE username = ?",
            ('admin',)
        )
        user = cursor.fetchone()
        
        if user:
            print(f"\n✅ Пароль обновлён успешно!")
            print(f"👤 Пользователь: {user[0]}")
            print(f"📧 Email: {user[1]}")
            print(f"🔑 Роль: {user[2]}")
            print(f"\n🔐 Данные для входа:")
            print(f"   Логин: admin")
            print(f"   Пароль: admin123")
        else:
            print("❌ Пользователь admin не найден!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    update_password()