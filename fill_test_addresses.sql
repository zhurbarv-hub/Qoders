-- Заполнение тестовыми адресами установки для существующих касс
UPDATE cash_registers 
SET installation_address = 'г. Москва, ул. Тестовая, д. ' || id::text 
WHERE installation_address IS NULL OR installation_address = '';

SELECT id, register_name, installation_address, model FROM cash_registers ORDER BY id;
