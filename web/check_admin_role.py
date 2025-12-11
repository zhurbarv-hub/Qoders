# -*- coding: utf-8 -*-
"""
Проверка и обновление роли администратора
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "kkt_system.db")

def check_admin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверка роли admin
    cursor.execute("SELECT id, username, role FROM web_users WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if admin:
        print(f"✅ Пользователь найден:")
        print(f"   ID: {admin[0]}")
        print(f"   Username: {admin[1]}")
        print(f"   Role: {admin[2]}")
        
        if admin[2] != 'admin':
            print(f"\n⚠️  Роль не 'admin'! Обновляем...")
            cursor.execute("UPDATE web_users SET role = 'admin' WHERE username = 'admin'")
            conn.commit()
            print(f"✅ Роль обновлена на 'admin'")
        else:
            print(f"\n✅ Роль правильная: 'admin'")
    else:
        print(f"❌ Пользователь 'admin' не найден!")
    
    conn.close()

if __name__ == "__main__":
    check_admin()