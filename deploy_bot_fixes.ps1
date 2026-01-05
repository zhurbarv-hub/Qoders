# PowerShell скрипт для деплоя исправлений Telegram бота на VDS

Write-Host "=" * 60
Write-Host "🚀 ДЕПЛОЙ ИСПРАВЛЕНИЙ TELEGRAM БОТА" -ForegroundColor Green
Write-Host "=" * 60

$VDS_HOST = "185.185.71.248"
$VDS_PORT = "40022"
$VDS_USER = "root"

# Файлы для деплоя
$files = @(
    @{
        local = "d:\QoProj\KKT\bot\services\notifier.py"
        remote = "/root/kkt_system/bot/services/notifier.py"
    },
    @{
        local = "d:\QoProj\KKT\bot\services\formatter.py"
        remote = "/root/kkt_system/bot/services/formatter.py"
    }
)

Write-Host ""
Write-Host "📤 Копирование файлов на VDS..." -ForegroundColor Cyan

foreach ($file in $files) {
    $fileName = Split-Path $file.local -Leaf
    Write-Host "  📄 $fileName" -ForegroundColor Yellow
    
    # Используем pscp если доступен, иначе scp
    $scpCommand = "scp"
    
    # Формируем команду
    $cmd = "$scpCommand -P $VDS_PORT `"$($file.local)`" ${VDS_USER}@${VDS_HOST}:$($file.remote)"
    
    Write-Host "    Выполняю: $cmd" -ForegroundColor Gray
    
    try {
        Invoke-Expression $cmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    ✅ Скопировано!" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️ Код возврата: $LASTEXITCODE" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "    ❌ Ошибка: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "🔄 Перезапуск Telegram бота..." -ForegroundColor Cyan
$restartCmd = "ssh -p $VDS_PORT ${VDS_USER}@${VDS_HOST} 'systemctl restart kkt_bot'"
Invoke-Expression $restartCmd

Write-Host ""
Write-Host "📊 Проверка статуса бота..." -ForegroundColor Cyan
$statusCmd = "ssh -p $VDS_PORT ${VDS_USER}@${VDS_HOST} 'systemctl status kkt_bot --no-pager | head -20'"
Invoke-Expression $statusCmd

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ ДЕПЛОЙ ЗАВЕРШЕН" -ForegroundColor Green
Write-Host "=" * 60

Write-Host ""
Write-Host "📝 Изменения:" -ForegroundColor Cyan
Write-Host "  1. Добавлен parse_mode='HTML' в send_notification()" -ForegroundColor White
Write-Host "  2. Улучшено форматирование уведомлений с детализацией" -ForegroundColor White
Write-Host "  3. Добавлены уровни срочности и призывы к действию" -ForegroundColor White
Write-Host ""
Write-Host "🔔 Теперь HTML-теги будут правильно отображаться!" -ForegroundColor Green
