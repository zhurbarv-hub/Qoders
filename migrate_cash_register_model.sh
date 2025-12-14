#!/bin/bash
set -e

echo "=== НАЧАЛО МИГРАЦИИ: Добавление поля 'модель ККТ' ==="
echo ""

# Шаг 1: Изменение типа поля model в cash_registers
echo "ШАГ 1: Изменяем тип поля model в cash_registers на VARCHAR(100)..."
sudo -u postgres psql -d kkt_production <<EOF
ALTER TABLE cash_registers ALTER COLUMN model TYPE VARCHAR(100);
EOF
echo "✓ Готово"
echo ""

# Шаг 2: Добавление поля cash_register_model в deadlines
echo "ШАГ 2: Добавляем поле cash_register_model в таблицу deadlines..."
sudo -u postgres psql -d kkt_production <<EOF
ALTER TABLE deadlines ADD COLUMN IF NOT EXISTS cash_register_model VARCHAR(100);
EOF
echo "✓ Готово"
echo ""

# Шаг 3: Заполнение данных
echo "ШАГ 3: Заполняем cash_register_model из связанных cash_registers..."
sudo -u postgres psql -d kkt_production <<EOF
UPDATE deadlines d 
SET cash_register_model = cr.model 
FROM cash_registers cr 
WHERE d.cash_register_id = cr.id AND d.cash_register_id IS NOT NULL;
EOF
echo "✓ Готово"
echo ""

# Шаг 4: Проверка изменений
echo "ШАГ 4: Проверка изменений в схеме БД..."
sudo -u postgres psql -d kkt_production <<EOF
SELECT 
    table_name,
    column_name, 
    data_type, 
    character_maximum_length as max_length
FROM information_schema.columns 
WHERE (table_name = 'cash_registers' AND column_name = 'model') 
   OR (table_name = 'deadlines' AND column_name = 'cash_register_model')
ORDER BY table_name, column_name;
EOF
echo ""

# Шаг 5: Пример данных
echo "ШАГ 5: Примеры обновленных данных..."
sudo -u postgres psql -d kkt_production <<EOF
SELECT 
    id, 
    client_id,
    cash_register_id, 
    cash_register_model, 
    expiration_date 
FROM deadlines 
WHERE cash_register_id IS NOT NULL 
LIMIT 5;
EOF
echo ""

echo "=== МИГРАЦИЯ БД ЗАВЕРШЕНА! ==="
