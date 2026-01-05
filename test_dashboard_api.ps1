# Проверка API статистики
Write-Host "=== Тест статистики ===" -ForegroundColor Cyan

# Логин
$loginBody = '{"username":"eliseev","password":"eliseev"}'
$loginResponse = Invoke-RestMethod -Uri "http://185.185.71.248:8080/api/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access_token

# Статистика
$headers = @{ "Authorization" = "Bearer $token" }
$stats = Invoke-RestMethod -Uri "http://185.185.71.248:8080/api/dashboard/stats" -Method Get -Headers $headers

Write-Host "`n📊 Всего клиентов: $($stats.total_clients)" -ForegroundColor White
Write-Host "💰 Всего касс: $($stats.total_cash_registers)" -ForegroundColor Cyan
Write-Host "📅 Всего дедлайнов: $($stats.total_deadlines)" -ForegroundColor White

if ($stats.total_cash_registers -eq 4) {
    Write-Host "`n✅ ТЕСТ ПРОЙДЕН!" -ForegroundColor Green
}
