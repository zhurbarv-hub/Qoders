# -*- coding: utf-8 -*-
"""
Применение миграции для создания таблицы web_users
"""
import sqlite3
import os

# Путь к базе данных
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "kkt_system.db")

# SQL миграция
MIGRATION_SQL = """
-- Создание таблицы пользователей веб-интерфейса
CREATE TABLE IF NOT EXISTS web_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    telegram_id VARCHAR(50) UNIQUE,
    last_login DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_web_users_username ON web_users(username);
CREATE INDEX IF NOT EXISTS idx_web_users_email ON web_users(email);
CREATE INDEX IF NOT EXISTS idx_web_users_role ON web_users(role);
CREATE INDEX IF NOT EXISTS idx_web_users_is_active ON web_users(is_active);

-- Вставка пользователя admin (пароль: admin123)
INSERT OR IGNORE INTO web_users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'admin',
    'admin@kkt-system.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYdNX.Jxnae',
    'Администратор',
    'admin',
    1
);
"""

def apply_migration():
    """Применить миграцию к базе данных"""
    print(f"📁 База данных: {DATABASE_PATH}")
    print(f"📊 Файл существует: {'✓' if os.path.exists(DATABASE_PATH) else '✗'}")
    
    try:
        # Подключение к БД
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Выполнение миграции
        print("\n🔄 Применение миграции...")
        cursor.executescript(MIGRATION_SQL)
        conn.commit()
        
        # Проверка результата
        cursor.execute("SELECT COUNT(*) FROM web_users")
        count = cursor.fetchone()[0]
        
        print(f"✅ Миграция применена успешно!")
        print(f"👥 Пользователей в таблице: {count}")
        
        if count > 0:
            cursor.execute("SELECT username, role FROM web_users")
            users = cursor.fetchall()
            print("\n📋 Список пользователей:")
            for username, role in users:
                print(f"  • {username} ({role})")
        
        conn.close()
        print("\n✅ Готово! Теперь можно войти с логином: admin, паролем: admin123")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    return True

if __name__ == "__main__":
    apply_migration()