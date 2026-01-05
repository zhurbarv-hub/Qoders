Write-Host "=== Проверка стилей для 1920x1080 ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1] Проверка загрузки CSS..." -ForegroundColor Yellow
ssh root@185.185.71.248 "ls -lh /home/kktapp/kkt-system/web/app/static/css/styles.css"

Write-Host ""
Write-Host "[2] Проверка размера файла..." -ForegroundColor Yellow  
ssh root@185.185.71.248 "wc -l /home/kktapp/kkt-system/web/app/static/css/styles.css"

Write-Host ""
Write-Host "[3] Проверка медиа-запросов для 1920px..." -ForegroundColor Yellow
ssh root@185.185.71.248 "grep -n '@media (min-width: 1920px)' /home/kktapp/kkt-system/web/app/static/css/styles.css"

Write-Host ""
Write-Host "[4] Проверка стилей .mdl-grid..." -ForegroundColor Yellow
ssh root@185.185.71.248 "grep -A 5 'Исправление для карточек статистики' /home/kktapp/kkt-system/web/app/static/css/styles.css"

Write-Host ""
Write-Host "=== Проверка завершена ===" -ForegroundColor Green
Write-Host ""
Write-Host "Теперь откройте https://kkt-box.net на мониторе 1920x1080" -ForegroundColor Yellow
Write-Host "Нажмите Ctrl+Shift+R для жесткой перезагрузки и очистки кэша" -ForegroundColor Yellow
