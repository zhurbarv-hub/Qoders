# Тест API статистики касс
Write-Host "=== Тест статистики дашборда ===" -ForegroundColor Cyan
Write-Host ""

# Шаг 1: Логин
Write-Host "[1/2] Авторизация..." -ForegroundColor Yellow
$loginBody = @{
    username = "eliseev"
    password = "eliseev"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://185.185.71.248:8080/api/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody
    
    $token = $response.access_token
    Write-Host "✅ Токен получен" -ForegroundColor Green
}
catch {
    Write-Host "❌ Ошибка авторизации: $_" -ForegroundColor Red
    exit 1
}

# Шаг 2: Получение статистики
Write-Host "`n[2/2] Получение статистики..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $stats = Invoke-RestMethod -Uri "http://185.185.71.248:8080/api/dashboard/stats" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✅ Статистика получена:" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Всего клиентов: $($stats.total_clients)" -ForegroundColor White
    Write-Host "✅ Активных клиентов: $($stats.active_clients)" -ForegroundColor White
    Write-Host "💰 Всего касс: $($stats.total_cash_registers)" -ForegroundColor Cyan
    Write-Host "📅 Всего дедлайнов: $($stats.total_deadlines)" -ForegroundColor White
    Write-Host "⏰ Активных дедлайнов: $($stats.active_deadlines)" -ForegroundColor White
    Write-Host "🟢 Норма: $($stats.status_green)" -ForegroundColor Green
    Write-Host "🟡 Внимание: $($stats.status_yellow)" -ForegroundColor Yellow
    Write-Host "🔴 Срочно: $($stats.status_red)" -ForegroundColor Red
    Write-Host "⚫ Просрочено: $($stats.status_expired)" -ForegroundColor Gray
    
    if ($stats.total_cash_registers -eq 4) {
        Write-Host "`n✅ ТЕСТ ПРОЙДЕН! Количество касс корректно: 4" -ForegroundColor Green
    }
    else {
        Write-Host "`n⚠️ ВНИМАНИЕ! Ожидалось 4 кассы, получено: $($stats.total_cash_registers)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Ошибка получения статистики: $_" -ForegroundColor Red
    exit 1
}
