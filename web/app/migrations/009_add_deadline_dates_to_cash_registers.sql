-- ============================================
-- Миграция 009: Добавление полей дат дедлайнов в cash_registers
-- Дата: 2025-12-13
-- Описание: Добавление полей fn_replacement_date и ofd_renewal_date
--           для автоматического управления дедлайнами кассовых аппаратов
-- ============================================

-- Шаг 1: Добавление колонки fn_replacement_date (дата замены фискального накопителя)
ALTER TABLE cash_registers ADD COLUMN fn_replacement_date DATE;

-- Шаг 2: Добавление колонки ofd_renewal_date (дата продления договора с ОФД)
ALTER TABLE cash_registers ADD COLUMN ofd_renewal_date DATE;

-- ============================================
-- Опциональная обратная миграция данных
-- ============================================
-- Если в системе уже есть дедлайны типа "Замена ФН", привязанные к кассам,
-- можно заполнить поле fn_replacement_date на основе существующих дедлайнов

/*
UPDATE cash_registers
SET fn_replacement_date = (
    SELECT d.expiration_date 
    FROM deadlines d
    JOIN deadline_types dt ON d.deadline_type_id = dt.id
    WHERE d.cash_register_id = cash_registers.id 
    AND dt.type_name = 'Замена ФН'
    AND d.status = 'active'
    LIMIT 1
);

UPDATE cash_registers
SET ofd_renewal_date = (
    SELECT d.expiration_date 
    FROM deadlines d
    JOIN deadline_types dt ON d.deadline_type_id = dt.id
    WHERE d.cash_register_id = cash_registers.id 
    AND dt.type_name LIKE '%продлен%'
    AND d.status = 'active'
    LIMIT 1
);
*/

-- ============================================
-- Проверка миграции
-- ============================================
-- Проверка структуры таблицы
-- PRAGMA table_info(cash_registers);

-- ============================================
-- План отката (Rollback)
-- ============================================
/*
-- SQLite не поддерживает ALTER TABLE DROP COLUMN напрямую
-- Для отката нужно пересоздать таблицу без новых колонок

CREATE TABLE cash_registers_backup AS SELECT 
    id, user_id, serial_number, fiscal_drive_number, 
    installation_address, register_name, ofd_provider_id, 
    notes, is_active, created_at, updated_at
FROM cash_registers;

DROP TABLE cash_registers;

ALTER TABLE cash_registers_backup RENAME TO cash_registers;

-- Восстановить индексы и constraints после отката
*/
