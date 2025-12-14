Write-Host "=== Uploading Cash Register Model UI Updates ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload updated HTML
Write-Host "[1/3] Uploading client-details.html..." -ForegroundColor Yellow
scp "d:\QoProj\KKT\web\app\static\client-details.html" root@185.185.71.248:/home/kktapp/kkt-system/web/app/static/

# Step 2: Upload updated JavaScript
Write-Host "[2/3] Uploading client-details.js..." -ForegroundColor Yellow
scp "d:\QoProj\KKT\web\app\static\js\client-details.js" root@185.185.71.248:/home/kktapp/kkt-system/web/app/static/js/

# Step 3: Restart web service
Write-Host "[3/3] Restarting web service..." -ForegroundColor Yellow
ssh root@185.185.71.248 "systemctl restart kkt-web.service; sleep 2; systemctl status kkt-web.service --no-pager"

Write-Host ""
Write-Host "=== COMPLETED! ===" -ForegroundColor Green
Write-Host "Cash register model field added to UI:" -ForegroundColor Green
Write-Host "  - Form for cash register: 'Название кассы' + 'Модель ККТ' (separate fields)" -ForegroundColor White
Write-Host "  - Form for deadline: 'Модель ККТ' field added (auto-fills from selected cash register)" -ForegroundColor White
