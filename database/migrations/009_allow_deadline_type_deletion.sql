-- ============================================
-- Миграция 009: Разрешение удаления типов услуг
-- Дата: 2025-12-13
-- Описание: Изменение deadline_type_id на nullable и удаление RESTRICT
-- ============================================

-- Шаг 1: Отключить проверку внешних ключей
PRAGMA foreign_keys = OFF;

-- Шаг 2: Создать новую таблицу deadlines с nullable deadline_type_id
CREATE TABLE deadlines_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    client_id INTEGER,
    deadline_type_id INTEGER,  -- Теперь NULL разрешен
    expiration_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cash_register_id INTEGER,
    
    -- Foreign keys без RESTRICT для deadline_type_id
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (cash_register_id) REFERENCES cash_registers(id) ON DELETE CASCADE
    -- deadline_type_id намеренно без FK constraint для свободного удаления типов
);

-- Шаг 3: Скопировать данные из старой таблицы
INSERT INTO deadlines_new (
    id, user_id, client_id, deadline_type_id, expiration_date, 
    status, notes, created_at, updated_at, cash_register_id
)
SELECT 
    id, user_id, client_id, deadline_type_id, expiration_date,
    status, notes, created_at, updated_at, cash_register_id
FROM deadlines;

-- Шаг 4: Удалить старую таблицу
DROP TABLE deadlines;

-- Шаг 5: Переименовать новую таблицу
ALTER TABLE deadlines_new RENAME TO deadlines;

-- Шаг 6: Восстановить индексы
CREATE INDEX idx_deadlines_user ON deadlines(user_id);
CREATE INDEX idx_deadlines_client ON deadlines(client_id);
CREATE INDEX idx_deadlines_type ON deadlines(deadline_type_id);
CREATE INDEX idx_deadlines_expiration ON deadlines(expiration_date);
CREATE INDEX idx_deadlines_status ON deadlines(status);
CREATE INDEX idx_deadlines_cash_register ON deadlines(cash_register_id);

-- Шаг 7: Включить проверку внешних ключей
PRAGMA foreign_keys = ON;

-- ============================================
-- Проверка миграции
-- ============================================

-- Проверить структуру таблицы
-- PRAGMA table_info(deadlines);

-- Проверить внешние ключи
-- PRAGMA foreign_key_list(deadlines);

-- Проверить количество записей
-- SELECT COUNT(*) FROM deadlines;

-- ============================================
-- Информация о миграции
-- ============================================

/*
Эта миграция:
1. Делает поле deadline_type_id nullable (разрешает NULL)
2. Удаляет constraint RESTRICT для deadline_type_id
3. Позволяет удалять типы услуг без блокировки
4. Сохраняет все существующие данные
5. Восстанавливает все индексы

После применения:
- Типы услуг можно удалять свободно
- При удалении типа нужно вручную очистить deadline_type_id в связанных дедлайнах
  (это делается в API endpoint)
- Дедлайны могут существовать без привязки к типу услуги
*/
