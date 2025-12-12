"""
Скрипт для применения миграции 007_unify_users_clients.sql
"""
import sqlite3
from pathlib import Path

def apply_migration():
    """Применить миграцию базы данных"""
    
    db_path = 'backend/kkt_service.db'
    migration_path = 'backend/migrations/007_unify_users_clients.sql'
    
    print("=" * 60)
    print("ПРИМЕНЕНИЕ МИГРАЦИИ 007: ОБЪЕДИНЕНИЕ USERS И CLIENTS")
    print("=" * 60)
    
    # Проверка существования файлов
    if not Path(db_path).exists():
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    if not Path(migration_path).exists():
        print(f"❌ Файл миграции не найден: {migration_path}")
        return False
    
    # Подключение к БД
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверка текущего состояния
        print("\n📊 Состояние БД до миграции:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"  Таблицы: {', '.join([t[0] for t in tables])}")
        
        # Проверка структуры users
        cursor.execute("PRAGMA table_info(users)")
        user_columns = cursor.fetchall()
        print(f"  Поля в users: {len(user_columns)}")
        for col in user_columns:
            print(f"    - {col[1]} ({col[2]})")
        
        # Чтение скрипта миграции
        print(f"\n📖 Чтение миграции: {migration_path}")
        migration_sql = Path(migration_path).read_text(encoding='utf-8')
        
        # Применение миграции
        print("\n⚙️  Применение миграции...")
        cursor.executescript(migration_sql)
        conn.commit()
        
        # Проверка результата
        print("\n✅ Миграция успешно применена!")
        print("\n📊 Состояние БД после миграции:")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables_after = cursor.fetchall()
        print(f"  Таблицы: {', '.join([t[0] for t in tables_after])}")
        
        cursor.execute("PRAGMA table_info(users)")
        user_columns_after = cursor.fetchall()
        print(f"\n  Новая структура users: {len(user_columns_after)} полей")
        for col in user_columns_after:
            print(f"    - {col[1]} ({col[2]})")
        
        # Статистика данных
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='client'")
        clients = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='manager'")
        managers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
        admins = cursor.fetchone()[0]
        
        print(f"\n📈 Статистика пользователей:")
        print(f"  Всего: {total_users}")
        print(f"  Клиентов: {clients}")
        print(f"  Менеджеров: {managers}")
        print(f"  Администраторов: {admins}")
        
        cursor.execute("SELECT COUNT(*) FROM deadlines WHERE user_id IS NOT NULL")
        deadlines_migrated = cursor.fetchone()[0]
        print(f"\n📋 Дедлайнов с привязкой к пользователям: {deadlines_migrated}")
        
        print("\n" + "=" * 60)
        print("✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ПРИМЕНЕНИИ МИГРАЦИИ:")
        print(f"  {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()
