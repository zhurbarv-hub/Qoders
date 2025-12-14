-- Обновление типов дедлайнов - делаем их пользовательскими (НЕ системными)
-- Теперь пользователь может редактировать и удалять эти типы

UPDATE deadline_types 
SET is_system = false,
    description = 'Тип дедлайна для отслеживания замены фискального накопителя'
WHERE type_name = 'Замена ФН';

UPDATE deadline_types 
SET is_system = false,
    description = 'Тип дедлайна для отслеживания продления договора с оператором фискальных данных'
WHERE type_name = 'Продление договора ОФД';

-- Проверка результата
SELECT id, type_name, is_system, is_active 
FROM deadline_types 
WHERE type_name IN ('Замена ФН', 'Продление договора ОФД')
ORDER BY type_name;
