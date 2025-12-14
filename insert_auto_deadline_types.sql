-- Создание типов дедлайнов для автоматического создания при добавлении касс
INSERT INTO deadline_types (type_name, description, is_active) VALUES
('Замена ФН', 'Автоматически создаётся при добавлении кассы с датой окончания ФН', true),
('Продление договора ОФД', 'Автоматически создаётся при добавлении кассы с датой окончания договора ОФД', true)
ON CONFLICT (type_name) DO UPDATE SET
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active;
