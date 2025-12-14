-- Проверка типов дедлайнов для автоматического создания
SELECT id, type_name, is_active 
FROM deadline_types 
WHERE type_name IN ('Замена ФН', 'Продление договора ОФД') 
ORDER BY type_name;
