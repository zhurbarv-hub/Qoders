-- Сделать все типы услуг пользовательскими, кроме "Замена ФН" и "Продление договора ОФД"
UPDATE deadline_types 
SET is_system = false 
WHERE type_name NOT IN ('Замена ФН', 'Продление договора ОФД');

-- Убедиться, что системные типы остаются системными
UPDATE deadline_types 
SET is_system = true 
WHERE type_name IN ('Замена ФН', 'Продление договора ОФД');

-- Проверка результата
SELECT id, type_name, is_system FROM deadline_types ORDER BY id;
