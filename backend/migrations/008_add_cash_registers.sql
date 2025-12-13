-- ============================================
-- Миграция 008: Добавление кассовых аппаратов
-- Дата: 2025-12-12
-- Описание: Создание таблицы cash_registers и расширение deadlines
-- ============================================

-- Шаг 1: Создание таблицы cash_registers
CREATE TABLE IF NOT EXISTS cash_registers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    fiscal_drive_number VARCHAR(50) NOT NULL,
    installation_address TEXT,
    register_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check constraints
    CHECK (length(fiscal_drive_number) >= 1),
    CHECK (length(register_name) >= 1)
);

-- Шаг 2: Создание индексов для cash_registers
CREATE INDEX IF NOT EXISTS idx_cash_registers_user ON cash_registers(user_id);
CREATE INDEX IF NOT EXISTS idx_cash_registers_serial ON cash_registers(serial_number);
CREATE INDEX IF NOT EXISTS idx_cash_registers_active ON cash_registers(is_active);

-- Шаг 3: Добавление колонки cash_register_id в таблицу deadlines
ALTER TABLE deadlines ADD COLUMN cash_register_id INTEGER;

-- Шаг 4: Создание индекса для cash_register_id
CREATE INDEX IF NOT EXISTS idx_deadlines_cash_register ON deadlines(cash_register_id);

-- Шаг 5: Добавление foreign key constraint для cash_register_id
-- Примечание: SQLite не поддерживает ALTER TABLE ADD CONSTRAINT для FK,
-- поэтому используем PRAGMA foreign_keys для проверки целостности

-- Проверка целостности данных
PRAGMA foreign_key_check(deadlines);

-- ============================================
-- Тестовые запросы для проверки миграции
-- ============================================

-- Проверка структуры таблицы cash_registers
-- SELECT sql FROM sqlite_master WHERE name='cash_registers';

-- Проверка индексов
-- SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='cash_registers';

-- Проверка новой колонки в deadlines
-- PRAGMA table_info(deadlines);

-- ============================================
-- План отката (Rollback)
-- ============================================

/*
-- Удаление индекса для cash_register_id
DROP INDEX IF EXISTS idx_deadlines_cash_register;

-- Создание новой таблицы deadlines без cash_register_id
CREATE TABLE deadlines_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    client_id INTEGER,
    deadline_type_id INTEGER NOT NULL,
    expiration_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (deadline_type_id) REFERENCES deadline_types(id) ON DELETE RESTRICT
);

-- Копирование данных из старой таблицы (без cash_register_id)
INSERT INTO deadlines_new (id, user_id, client_id, deadline_type_id, expiration_date, status, notes, created_at, updated_at)
SELECT id, user_id, client_id, deadline_type_id, expiration_date, status, notes, created_at, updated_at
FROM deadlines;

-- Удаление старой таблицы
DROP TABLE deadlines;

-- Переименование новой таблицы
ALTER TABLE deadlines_new RENAME TO deadlines;

-- Восстановление индексов для deadlines
CREATE INDEX idx_deadlines_client ON deadlines(client_id);
CREATE INDEX idx_deadlines_user ON deadlines(user_id);
CREATE INDEX idx_deadlines_expiration ON deadlines(expiration_date);
CREATE INDEX idx_deadlines_status ON deadlines(status);
CREATE INDEX idx_deadlines_type ON deadlines(deadline_type_id);

-- Удаление таблицы cash_registers
DROP TABLE IF EXISTS cash_registers;
*/
