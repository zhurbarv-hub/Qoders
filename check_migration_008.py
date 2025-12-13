"""
Проверка структуры БД и применение миграции 008
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'web' / 'database' / 'kkt_services.db'

def check_and_apply_migration():
    """Проверить БД и применить миграцию если необходимо"""
    print("=" * 60)
    print("Проверка и применение миграции 008")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    # Проверяем существование таблицы cash_registers
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cash_registers'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("✓ Таблица cash_registers уже существует")
    else:
        print("⚠  Таблица cash_registers не найдена, создаем...")
        
        # Создаем таблицу
        cursor.execute("""
            CREATE TABLE cash_registers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                serial_number VARCHAR(50) NOT NULL UNIQUE,
                fiscal_drive_number VARCHAR(50) NOT NULL,
                installation_address TEXT,
                register_name VARCHAR(100) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CHECK (length(fiscal_drive_number) >= 1),
                CHECK (length(register_name) >= 1)
            )
        """)
        print("✓ Таблица cash_registers создана")
        
        # Создаем индексы
        cursor.execute("CREATE INDEX idx_cash_registers_user ON cash_registers(user_id)")
        cursor.execute("CREATE INDEX idx_cash_registers_serial ON cash_registers(serial_number)")
        cursor.execute("CREATE INDEX idx_cash_registers_active ON cash_registers(is_active)")
        print("✓ Индексы созданы")
    
    # Проверяем колонку cash_register_id в deadlines
    cursor.execute("PRAGMA table_info(deadlines)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'cash_register_id' in columns:
        print("✓ Колонка cash_register_id уже существует в deadlines")
    else:
        print("⚠  Колонка cash_register_id не найдена, добавляем...")
        cursor.execute("ALTER TABLE deadlines ADD COLUMN cash_register_id INTEGER")
        cursor.execute("CREATE INDEX idx_deadlines_cash_register ON deadlines(cash_register_id)")
        print("✓ Колонка cash_register_id добавлена в deadlines")
    
    conn.commit()
    
    # Итоговая проверка
    print("\n" + "=" * 60)
    print("Итоговая проверка:")
    print("=" * 60)
    
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='cash_registers'")
    result = cursor.fetchone()
    if result:
        print("✓ cash_registers: OK")
    
    cursor.execute("PRAGMA table_info(deadlines)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'cash_register_id' in columns:
        print("✓ deadlines.cash_register_id: OK")
    
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name='cash_registers'")
    index_count = cursor.fetchone()[0]
    print(f"✓ Индексов cash_registers: {index_count}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Миграция 008 завершена успешно!")
    print("=" * 60)

if __name__ == "__main__":
    check_and_apply_migration()
