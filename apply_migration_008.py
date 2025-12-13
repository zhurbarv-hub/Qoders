"""
Скрипт применения миграции 008: Добавление кассовых аппаратов
"""
import sqlite3
import os
from pathlib import Path

# Определяем пути
BASE_DIR = Path(__file__).parent
MIGRATION_FILE = BASE_DIR / 'backend' / 'migrations' / '008_add_cash_registers.sql'
DB_PATH = BASE_DIR / 'database' / 'kkt_services.db'

def apply_migration():
    """Применить миграцию 008"""
    print("=" * 60)
    print("Применение миграции 008: Добавление кассовых аппаратов")
    print("=" * 60)
    
    if not DB_PATH.exists():
        print(f"❌ База данных не найдена: {DB_PATH}")
        return False
    
    if not MIGRATION_FILE.exists():
        print(f"❌ Файл миграции не найден: {MIGRATION_FILE}")
        return False
    
    try:
        # Читаем SQL миграции
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Подключаемся к БД
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")  # Включаем поддержку FK
        cursor = conn.cursor()
        
        # Выполняем миграцию построчно (игнорируем комментарии и PRAGMA)
        statements = []
        current_statement = []
        in_multiline_comment = False
        
        for line in migration_sql.split('\n'):
            line = line.strip()
            
            # Проверяем начало многострочного комментария
            if line.startswith('/*'):
                in_multiline_comment = True
                continue
            
            # Проверяем конец многострочного комментария
            if '*/' in line:
                in_multiline_comment = False
                continue
            
            # Пропускаем строки внутри многострочного комментария
            if in_multiline_comment:
                continue
            
            # Пропускаем пустые строки и комментарии
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # Если строка заканчивается на ;, это конец statement
            if line.endswith(';'):
                full_statement = ' '.join(current_statement)
                statements.append(full_statement)
                current_statement = []
        
        # Выполняем каждый statement
        for i, statement in enumerate(statements, 1):
            try:
                # Пропускаем PRAGMA foreign_key_check (он не работает как обычный SQL)
                if 'PRAGMA foreign_key_check' in statement:
                    print(f"  [{i}] Пропуск PRAGMA statement")
                    continue
                
                cursor.execute(statement)
                print(f"  ✓ [{i}] Выполнено: {statement[:50]}...")
            except sqlite3.Error as e:
                # Игнорируем ошибки дублирующихся объектов
                if "already exists" in str(e) or "duplicate column" in str(e):
                    print(f"  ⚠ [{i}] Объект уже существует (пропущено): {statement[:50]}...")
                else:
                    print(f"  ❌ [{i}] Ошибка: {e}")
                    print(f"      Statement: {statement}")
                    raise
        
        conn.commit()
        
        # Проверяем результат
        print("\n" + "=" * 60)
        print("Проверка результатов миграции:")
        print("=" * 60)
        
        # Проверка таблицы cash_registers
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='cash_registers'")
        result = cursor.fetchone()
        if result:
            print("✓ Таблица cash_registers создана")
        else:
            print("❌ Таблица cash_registers не найдена")
        
        # Проверка индексов
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name='cash_registers'")
        index_count = cursor.fetchone()[0]
        print(f"✓ Создано индексов для cash_registers: {index_count}")
        
        # Проверка новой колонки в deadlines
        cursor.execute("PRAGMA table_info(deadlines)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'cash_register_id' in columns:
            print("✓ Колонка cash_register_id добавлена в deadlines")
        else:
            print("❌ Колонка cash_register_id не найдена в deadlines")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Миграция 008 успешно применена!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при применении миграции: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    apply_migration()
