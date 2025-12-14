Write-Host "=== МИГРАЦИЯ: Добавление поля 'модель ККТ' ===" -ForegroundColor Cyan
Write-Host ""

# Загружаем bash скрипт миграции
Write-Host "[1/5] Загрузка скрипта миграции БД..." -ForegroundColor Yellow
scp "d:\QoProj\KKT\migrate_cash_register_model.sh" root@185.185.71.248:/tmp/migrate_model.sh
if ($LASTEXITCODE -eq 0) { Write-Host "✓ Скрипт загружен" -ForegroundColor Green } else { exit 1 }
Write-Host ""

# Выполняем миграцию БД
Write-Host "[2/5] Выполнение миграции БД..." -ForegroundColor Yellow
ssh root@185.185.71.248 "chmod +x /tmp/migrate_model.sh && /tmp/migrate_model.sh"
if ($LASTEXITCODE -eq 0) { Write-Host "✓ Миграция БД завершена" -ForegroundColor Green } else { exit 1 }
Write-Host ""

# Загружаем обновленные модели Python
Write-Host "[3/5] Загрузка обновленных моделей Python..." -ForegroundColor Yellow
scp "d:\QoProj\KKT\web\app\models\client.py" root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/client.py
scp "d:\QoProj\KKT\web\app\models\cash_register.py" root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/cash_register.py
if ($LASTEXITCODE -eq 0) { Write-Host "✓ Модели загружены" -ForegroundColor Green } else { exit 1 }
Write-Host ""

# Устанавливаем права
Write-Host "[4/5] Установка прав доступа..." -ForegroundColor Yellow
ssh root@185.185.71.248 "chown -R kktapp:kktapp /home/kktapp/kkt-system/web/app/models/"
if ($LASTEXITCODE -eq 0) { Write-Host "✓ Права установлены" -ForegroundColor Green } else { exit 1 }
Write-Host ""

# Перезапускаем веб-сервис
Write-Host "[5/5] Перезапуск веб-сервиса..." -ForegroundColor Yellow
ssh root@185.185.71.248 "systemctl restart kkt-web.service && sleep 2 && systemctl status kkt-web.service --no-pager | head -10"
if ($LASTEXITCODE -eq 0) { Write-Host "✓ Сервис перезапущен" -ForegroundColor Green } else { Write-Host "! Проверьте статус сервиса" -ForegroundColor Red }
Write-Host ""

Write-Host "=== ВСЕ ГОТОВО! ===" -ForegroundColor Green
Write-Host "Поле 'модель ККТ' добавлено в таблицы cash_registers и deadlines" -ForegroundColor Cyan
