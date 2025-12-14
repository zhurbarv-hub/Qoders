Write-Host "=== MIGRATION: Adding cash register model field ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload migration script
Write-Host "[1/5] Uploading DB migration script..." -ForegroundColor Yellow
scp "d:\QoProj\KKT\migrate_cash_register_model.sh" root@185.185.71.248:/tmp/migrate_model.sh
Write-Host ""

# Step 2: Execute DB migration
Write-Host "[2/5] Executing DB migration..." -ForegroundColor Yellow  
ssh root@185.185.71.248 "chmod +x /tmp/migrate_model.sh; /tmp/migrate_model.sh"
Write-Host ""

# Step 3: Upload updated Python models
Write-Host "[3/5] Uploading updated Python models..." -ForegroundColor Yellow
scp "d:\QoProj\KKT\web\app\models\client.py" root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/client.py
scp "d:\QoProj\KKT\web\app\models\cash_register.py" root@185.185.71.248:/home/kktapp/kkt-system/web/app/models/cash_register.py
Write-Host ""

# Step 4: Set permissions
Write-Host "[4/5] Setting permissions..." -ForegroundColor Yellow
ssh root@185.185.71.248 "chown -R kktapp:kktapp /home/kktapp/kkt-system/web/app/models/"
Write-Host ""

# Step 5: Restart web service
Write-Host "[5/5] Restarting web service..." -ForegroundColor Yellow
ssh root@185.185.71.248 "systemctl restart kkt-web.service; sleep 2; systemctl status kkt-web.service --no-pager"
Write-Host ""

Write-Host "=== COMPLETED! ===" -ForegroundColor Green
