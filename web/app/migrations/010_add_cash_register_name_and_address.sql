-- Миграция 010: Добавление полей register_name и installation_address в таблицу cash_registers
-- Дата: 2025-12-14
-- Описание: Добавляем поддержку пользовательского названия кассы и адреса установки

-- Добавление новых столбцов
ALTER TABLE cash_registers 
ADD COLUMN IF NOT EXISTS register_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS installation_address TEXT;

-- Для обратной совместимости: заполняем register_name значением model для существующих записей
UPDATE cash_registers 
SET register_name = model 
WHERE register_name IS NULL AND model IS NOT NULL AND model != '';

-- Комментарии к столбцам
COMMENT ON COLUMN cash_registers.register_name IS 'Пользовательское название кассы (например, "Касса №1 на складе")';
COMMENT ON COLUMN cash_registers.installation_address IS 'Адрес установки кассового аппарата';
