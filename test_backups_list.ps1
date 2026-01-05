$loginBody = '{"username":"eliseev","password":"eliseev"}'
$loginResponse = Invoke-RestMethod -Uri "http://185.185.71.248:8080/api/auth/login" -Method Post -ContentType "application/json" -Body $loginBody -ErrorAction Stop
$token = $loginResponse.access_token

$headers = @{ "Authorization" = "Bearer $token" }
$backups = Invoke-RestMethod -Uri "http://185.185.71.248:8080/api/database/backups" -Method Get -Headers $headers -ErrorAction Stop

Write-Host "Total backups: $($backups.total_count)"
Write-Host ""
foreach ($backup in $backups.backups) {
    Write-Host "File: $($backup.filename)"
    Write-Host "  Created: $($backup.created_at)"
    Write-Host "  Size: $($backup.size_mb) MB"
    Write-Host "  By: $($backup.created_by)"
    Write-Host "  Desc: $($backup.description)"
    Write-Host ""
}
