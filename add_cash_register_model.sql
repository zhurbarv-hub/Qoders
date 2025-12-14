-- Миграция: добавление поля "модель ККТ" в таблицы cash_registers и deadlines

-- 1. Изменить тип поля model в таблице cash_registers (с VARCHAR(255) на VARCHAR(100))
ALTER TABLE cash_registers ALTER COLUMN model TYPE VARCHAR(100);

-- 2. Добавить поле cash_register_model в таблицу deadlines
ALTER TABLE deadlines ADD COLUMN IF NOT EXISTS cash_register_model VARCHAR(100);

-- 3. Заполнить поле cash_register_model из связанных cash_registers (для существующих записей)
UPDATE deadlines d
SET cash_register_model = cr.model
FROM cash_registers cr
WHERE d.cash_register_id = cr.id AND d.cash_register_id IS NOT NULL;

-- Проверка изменений
SELECT 
    'cash_registers.model' as field,
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'cash_registers' AND column_name = 'model'
UNION ALL
SELECT 
    'deadlines.cash_register_model' as field,
    data_type,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'deadlines' AND column_name = 'cash_register_model';

-- Вывод примера данных
SELECT id, cash_register_id, cash_register_model, expiration_date 
FROM deadlines 
WHERE cash_register_id IS NOT NULL 
LIMIT 5;
