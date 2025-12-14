-- Сделать поле deadline_type_id необязательным (nullable)
ALTER TABLE deadlines ALTER COLUMN deadline_type_id DROP NOT NULL;

-- Проверка изменения
SELECT 
    column_name, 
    is_nullable, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'deadlines' AND column_name = 'deadline_type_id';
