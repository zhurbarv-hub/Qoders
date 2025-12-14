$scriptContent = @'
sudo -u postgres psql -d kkt_production << 'EOF'
ALTER TABLE cash_registers ALTER COLUMN model TYPE VARCHAR(100);
ALTER TABLE deadlines ADD COLUMN IF NOT EXISTS cash_register_model VARCHAR(100);
UPDATE deadlines d SET cash_register_model = cr.model FROM cash_registers cr WHERE d.cash_register_id = cr.id AND d.cash_register_id IS NOT NULL;
SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE (table_name = 'cash_registers' AND column_name = 'model') OR (table_name = 'deadlines' AND column_name = 'cash_register_model');
EOF
'@

# Сохраняем во временный файл
$scriptContent | Out-File -FilePath "d:\QoProj\KKT\temp_migration.sh" -Encoding ASCII

# Загружаем на VDS
& scp "d:\QoProj\KKT\temp_migration.sh" root@185.185.71.248:/tmp/temp_migration.sh

# Выполняем
& ssh root@185.185.71.248 "chmod +x /tmp/temp_migration.sh && bash /tmp/temp_migration.sh"

Write-Host "Migration completed!"
