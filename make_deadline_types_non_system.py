# -*- coding: utf-8 -*-
"""
Скрипт для обновления всех типов услуг на несистемные (is_system = 0)

Использование:
    python make_deadline_types_non_system.py
"""

import sqlite3
import os
from pathlib import Path

def get_db_path():
    """Определить путь к базе данных"""
    # Попробуем найти БД в разных местах
    possible_paths = [
        'web/app/kkt.db',
        'web/kkt.db',
        'database/kkt.db',
        'kkt.db',
        '../kkt.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Если не нашли, спросим пользователя
    print("❌ База данных не найдена автоматически")
    db_path = input("Введите путь к базе данных (например, web/kkt.db): ").strip()
    if os.path.exists(db_path):
        return db_path
    else:
        raise FileNotFoundError(f"База данных не найдена по пути: {db_path}")


def make_types_non_system():
    """Обновить все типы услуг на несистемные"""
    
    print("=" * 80)
    print("🔧 ОБНОВЛЕНИЕ ТИПОВ УСЛУГ НА НЕСИСТЕМНЫЕ")
    print("=" * 80)
    
    try:
        # Получаем путь к БД
        db_path = get_db_path()
        print(f"\n📂 Используется БД: {db_path}")
        
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем текущее состояние
        print("\n📊 Текущее состояние типов услуг:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_system = 1 THEN 1 ELSE 0 END) as system_count,
                SUM(CASE WHEN is_system = 0 THEN 1 ELSE 0 END) as non_system_count
            FROM deadline_types
        """)
        
        total, system_count, non_system_count = cursor.fetchone()
        print(f"  📊 Всего типов: {total}")
        print(f"  🔒 Системных: {system_count}")
        print(f"  🔓 Несистемных: {non_system_count}")
        
        if system_count == 0:
            print("\n✅ Все типы услуг уже несистемные. Обновление не требуется.")
            conn.close()
            return
        
        # Показываем системные типы
        print(f"\n🔍 Системные типы (будут обновлены):")
        cursor.execute("""
            SELECT id, type_name, is_active
            FROM deadline_types
            WHERE is_system = 1
            ORDER BY id
        """)
        
        system_types = cursor.fetchall()
        for type_id, type_name, is_active in system_types:
            status = "✅ активен" if is_active else "❌ неактивен"
            print(f"  - ID {type_id}: {type_name} ({status})")
        
        # Запрашиваем подтверждение
        print(f"\n⚠️  Будет обновлено {system_count} типов услуг")
        confirm = input("Продолжить? (да/нет): ").strip().lower()
        
        if confirm not in ['да', 'yes', 'y', 'д']:
            print("\n❌ Операция отменена пользователем")
            conn.close()
            return
        
        # Выполняем обновление
        print("\n🔄 Обновление типов услуг...")
        cursor.execute("""
            UPDATE deadline_types
            SET is_system = 0
            WHERE is_system = 1
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ Успешно обновлено: {updated_count} типов")
        
        # Проверяем результат
        print("\n📊 Новое состояние типов услуг:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_system = 1 THEN 1 ELSE 0 END) as system_count,
                SUM(CASE WHEN is_system = 0 THEN 1 ELSE 0 END) as non_system_count
            FROM deadline_types
        """)
        
        total, system_count, non_system_count = cursor.fetchone()
        print(f"  📊 Всего типов: {total}")
        print(f"  🔒 Системных: {system_count}")
        print(f"  🔓 Несистемных: {non_system_count}")
        
        # Закрываем соединение
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print("=" * 80)
        print("\nТеперь все типы услуг можно удалять через интерфейс.")
        print("При удалении типа, поле deadline_type_id в связанных дедлайнах будет очищено.")
        
    except sqlite3.Error as e:
        print(f"\n❌ Ошибка при работе с базой данных: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        return False


if __name__ == "__main__":
    try:
        make_types_non_system()
    except KeyboardInterrupt:
        print("\n\n❌ Операция прервана пользователем (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
