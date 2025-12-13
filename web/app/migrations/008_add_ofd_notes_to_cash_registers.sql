-- Добавление полей ofd_name и notes в таблицу cash_registers

ALTER TABLE cash_registers ADD COLUMN ofd_name VARCHAR(200);
ALTER TABLE cash_registers ADD COLUMN notes TEXT;
