# -*- coding: utf-8 -*-
"""
Скрипт для автоматического обновления всех типов услуг на несистемные (is_system = 0)
"""

import sqlite3
import os

def make_types_non_system_auto():
    """Автоматически обновить все типы услуг на несистемные"""
    
    db_path = 'web/app/kkt.db'
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    print("=" * 80)
    print("🔧 АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ ТИПОВ УСЛУГ")
    print("=" * 80)
    print(f"\n📂 БД: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем текущее состояние
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_system = 1 THEN 1 ELSE 0 END) as system_count
            FROM deadline_types
        """)
        
        total, system_count = cursor.fetchone()
        print(f"\n📊 Всего типов: {total}")
        print(f"🔒 Системных: {system_count}")
        
        if system_count == 0:
            print("\n✅ Все типы уже несистемные")
            conn.close()
            return True
        
        # Показываем системные типы
        print(f"\n🔍 Системные типы:")
        cursor.execute("""
            SELECT id, type_name
            FROM deadline_types
            WHERE is_system = 1
            ORDER BY id
        """)
        
        for type_id, type_name in cursor.fetchall():
            print(f"  - ID {type_id}: {type_name}")
        
        # Обновляем
        print(f"\n🔄 Обновление {system_count} типов...")
        cursor.execute("""
            UPDATE deadline_types
            SET is_system = 0
            WHERE is_system = 1
        """)
        
        conn.commit()
        print(f"✅ Обновлено: {cursor.rowcount} типов")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ ГОТОВО!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    make_types_non_system_auto()
