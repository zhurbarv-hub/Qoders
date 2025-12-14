# Check nginx configuration on VDS and enable external access
# Run this script ON THE VDS SERVER via SSH

Write-Host "=== Checking nginx configuration on VDS ===" -ForegroundColor Cyan

# 1. Check nginx status
Write-Host "`n1. Checking nginx service status..." -ForegroundColor Yellow
ssh root@185.185.71.248 "systemctl status nginx --no-pager | head -20"

# 2. Check nginx configuration
Write-Host "`n2. Checking nginx configuration..." -ForegroundColor Yellow
ssh root@185.185.71.248 "nginx -t"

# 3. Check listening ports
Write-Host "`n3. Checking listening ports..." -ForegroundColor Yellow
ssh root@185.185.71.248 "netstat -tlnp | grep nginx"

# 4. Check nginx site configuration
Write-Host "`n4. Checking site configuration..." -ForegroundColor Yellow
ssh root@185.185.71.248 "ls -la /etc/nginx/sites-enabled/"

# 5. Check if kkt site exists
Write-Host "`n5. Checking KKT site config..." -ForegroundColor Yellow
ssh root@185.185.71.248 "cat /etc/nginx/sites-available/kkt* 2>/dev/null | head -50"

# 6. Check firewall
Write-Host "`n6. Checking firewall rules..." -ForegroundColor Yellow
ssh root@185.185.71.248 "ufw status | grep 8080"

# 7. Check kkt-web service
Write-Host "`n7. Checking kkt-web service..." -ForegroundColor Yellow
ssh root@185.185.71.248 "systemctl status kkt-web --no-pager | head -20"

Write-Host "`n=== Check complete ===" -ForegroundColor Cyan
