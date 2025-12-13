# -*- coding: utf-8 -*-
"""
Применение миграции 009: Разрешение удаления типов услуг
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'database/kkt_services.db'
MIGRATION_FILE = 'database/migrations/009_allow_deadline_type_deletion.sql'
BACKUP_DIR = 'backups'

def create_backup():
    """Создать резервную копию БД"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{BACKUP_DIR}/kkt_services_before_migration_009_{timestamp}.db'
    
    print(f"📦 Создание резервной копии: {backup_path}")
    
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    
    print(f"✅ Резервная копия создана")
    return backup_path


def apply_migration():
    """Применить миграцию"""
    
    print("=" * 80)
    print("ПРИМЕНЕНИЕ МИГРАЦИИ 009")
    print("=" * 80)
    
    # 1. Проверка файлов
    if not os.path.exists(DB_PATH):
        print(f"❌ База данных не найдена: {DB_PATH}")
        return False
    
    if not os.path.exists(MIGRATION_FILE):
        print(f"❌ Файл миграции не найден: {MIGRATION_FILE}")
        return False
    
    print(f"\n✅ База данных: {DB_PATH}")
    print(f"✅ Миграция: {MIGRATION_FILE}")
    
    # 2. Создать резервную копию
    try:
        backup_path = create_backup()
    except Exception as e:
        print(f"❌ Ошибка создания backup: {e}")
        return False
    
    # 3. Подключиться к БД
    print("\n📊 Проверка текущего состояния...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Проверить текущую структуру
        cursor.execute("PRAGMA table_info(deadlines)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        deadline_type_col = columns.get('deadline_type_id')
        if deadline_type_col:
            notnull = deadline_type_col[3]
            if notnull:
                print("  ⚠️ deadline_type_id: NOT NULL (требуется миграция)")
            else:
                print("  ✅ deadline_type_id: nullable (миграция уже применена?)")
                confirm = input("\n⚠️ Похоже миграция уже применена. Продолжить? (да/нет): ").strip().lower()
                if confirm not in ['да', 'yes', 'y', 'д']:
                    print("❌ Отменено")
                    conn.close()
                    return False
        
        # Проверить количество записей
        cursor.execute("SELECT COUNT(*) FROM deadlines")
        total_deadlines = cursor.fetchone()[0]
        print(f"  📊 Дедлайнов в БД: {total_deadlines}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False
    
    # 4. Применить миграцию
    print("\n🔄 Применение миграции...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Читаем и выполняем SQL миграцию
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Выполняем миграцию
        cursor.executescript(migration_sql)
        conn.commit()
        
        print("✅ Миграция применена")
        
    except Exception as e:
        print(f"❌ Ошибка применения миграции: {e}")
        print(f"\n📦 Восстановите БД из backup: {backup_path}")
        conn.rollback()
        conn.close()
        return False
    
    # 5. Проверить результат
    print("\n✅ Проверка результата...")
    try:
        cursor.execute("PRAGMA table_info(deadlines)")
        columns = {col[1]: col for col in cursor.fetchall()}
        
        deadline_type_col = columns.get('deadline_type_id')
        if deadline_type_col:
            notnull = deadline_type_col[3]
            if notnull:
                print("  ❌ deadline_type_id: все еще NOT NULL!")
            else:
                print("  ✅ deadline_type_id: nullable")
        
        # Проверить foreign keys
        cursor.execute("PRAGMA foreign_key_list(deadlines)")
        fks = cursor.fetchall()
        
        has_restrict = False
        for fk in fks:
            if fk[2] == 'deadline_types' and fk[6] == 'RESTRICT':
                has_restrict = True
                break
        
        if has_restrict:
            print("  ❌ Foreign key RESTRICT все еще есть!")
        else:
            print("  ✅ Foreign key RESTRICT удален")
        
        # Проверить количество записей
        cursor.execute("SELECT COUNT(*) FROM deadlines")
        new_total = cursor.fetchone()[0]
        print(f"  ✅ Дедлайнов после миграции: {new_total}")
        
        if new_total == total_deadlines:
            print(f"  ✅ Все данные сохранены ({new_total} записей)")
        else:
            print(f"  ❌ ПОТЕРЯ ДАННЫХ! Было: {total_deadlines}, стало: {new_total}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✅ МИГРАЦИЯ УСПЕШНО ПРИМЕНЕНА")
    print("=" * 80)
    print(f"\n📦 Резервная копия: {backup_path}")
    print("\nТеперь можно:")
    print("  1. Перезапустить веб-сервер")
    print("  2. Удалять типы услуг через API/UI")
    print("  3. Тестировать удаление типов с дедлайнами")
    
    return True


if __name__ == "__main__":
    try:
        success = apply_migration()
        if success:
            print("\n🎉 Готово!")
        else:
            print("\n❌ Миграция не применена")
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
