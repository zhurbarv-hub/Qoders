#!/bin/bash
# Обновление типов дедлайнов для автоматического создания

sudo -u postgres psql -d kkt_production <<EOF
UPDATE deadline_types 
SET is_system = true,
    description = 'Автоматически создаётся при добавлении/редактировании кассы из поля "Дата окончания ФН". Системный тип, неудаляемый.'
WHERE type_name = 'Замена ФН';

UPDATE deadline_types 
SET is_system = true,
    description = 'Автоматически создаётся при добавлении/редактировании кассы из поля "дата окончания ОФД". Системный тип, неудаляемый.'
WHERE type_name = 'Продление договора ОФД';

SELECT id, type_name, is_system, is_active, description 
FROM deadline_types 
WHERE type_name IN ('Замена ФН', 'Продление договора ОФД');
EOF

echo "Типы дедлайнов обновлены на системные (is_system = true)"
