# Выполнение миграции БД через SSH
$commands = @"
sudo -u postgres psql -d kkt_production -c "ALTER TABLE cash_registers ALTER COLUMN model TYPE VARCHAR(100);"
sudo -u postgres psql -d kkt_production -c "ALTER TABLE deadlines ADD COLUMN IF NOT EXISTS cash_register_model VARCHAR(100);"
sudo -u postgres psql -d kkt_production -c "UPDATE deadlines d SET cash_register_model = cr.model FROM cash_registers cr WHERE d.cash_register_id = cr.id AND d.cash_register_id IS NOT NULL;"
sudo -u postgres psql -d kkt_production -c "SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE (table_name = 'cash_registers' AND column_name = 'model') OR (table_name = 'deadlines' AND column_name = 'cash_register_model') ORDER BY table_name, column_name;"
"@

Write-Host "Выполнение миграции..." -ForegroundColor Green

# Сохраняем команды в файл
$commands | Out-File -FilePath "$PSScriptRoot\temp_commands.sh" -Encoding ASCII -NoNewline

# Загружаем на VDS  
Write-Host "Загрузка скрипта на VDS..."
& scp "$PSScriptRoot\temp_commands.sh" root@185.185.71.248:/tmp/migration_commands.sh 2>&1 | Write-Host

# Выполняем
Write-Host "Выполнение команд миграции..."
& ssh root@185.185.71.248 "bash /tmp/migration_commands.sh" 2>&1 | Write-Host

# Загружаем обновленные модели
Write-Host "`nЗагрузка обновленных моделей..."
& scp "$PSScriptRoot\web\app\models\client.py" root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/client.py 2>&1 | Write-Host
& scp "$PSScriptRoot\web\app\models\cash_register.py" root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/cash_register.py 2>&1 | Write-Host

# Устанавливаем права
Write-Host "`nУстановка прав..."
& ssh root@185.185.71.248 "chown -R kktapp:kktapp /home/kktapp/kkt-system/web/app/models/" 2>&1 | Write-Host

# Перезапускаем сервис
Write-Host "`nПерезапуск сервиса..."
& ssh root@185.185.71.248 "systemctl restart kkt-web.service" 2>&1 | Write-Host

# Проверяем статус
Write-Host "`nПроверка статуса сервиса..."
& ssh root@185.185.71.248 "systemctl status kkt-web.service --no-pager | head -15" 2>&1 | Write-Host

Write-Host "`n=== Миграция завершена! ===" -ForegroundColor Green

# Удаляем временный файл
Remove-Item "$PSScriptRoot\temp_commands.sh" -ErrorAction SilentlyContinue
