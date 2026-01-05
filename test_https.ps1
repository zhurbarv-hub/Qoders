Write-Host "=== Проверка HTTPS для kkt-box.net ===" -ForegroundColor Cyan
Write-Host ""

# Тест 1: HTTP редирект
Write-Host "[1] Тест HTTP → HTTPS редирект..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://kkt-box.net" -MaximumRedirection 0 -ErrorAction SilentlyContinue
    Write-Host "❌ Редирект не работает (код $($response.StatusCode))" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 301 -or $_.Exception.Response.StatusCode -eq 302) {
        $location = $_.Exception.Response.Headers['Location']
        Write-Host "✅ Редирект работает: $location" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Неожиданный ответ: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Тест 2: HTTPS доступность
Write-Host "[2] Тест HTTPS доступность..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://kkt-box.net" -TimeoutSec 10
    Write-Host "✅ HTTPS работает (код $($response.StatusCode))" -ForegroundColor Green
    Write-Host "    Content-Type: $($response.Headers['Content-Type'])" -ForegroundColor Gray
} catch {
    Write-Host "❌ HTTPS не доступен: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Тест 3: Проверка сертификата
Write-Host "[3] Информация о сертификате..." -ForegroundColor Yellow
ssh root@185.185.71.248 "certbot certificates 2>&1 | grep -A 6 'Certificate Name'"

Write-Host ""
Write-Host "=== Проверка завершена ===" -ForegroundColor Cyan
Write-Host "=== Проверка HTTPS для kkt-box.net ===" -ForegroundColor Cyan
Write-Host ""

# Тест 1: HTTP редирект
Write-Host "[1] Тест HTTP → HTTPS редирект..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://kkt-box.net" -MaximumRedirection 0 -ErrorAction SilentlyContinue
    Write-Host "❌ Редирект не работает (код $($response.StatusCode))" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 301 -or $_.Exception.Response.StatusCode -eq 302) {
        $location = $_.Exception.Response.Headers['Location']
        Write-Host "✅ Редирект работает: $location" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Неожиданный ответ: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""

# Тест 2: HTTPS доступность
Write-Host "[2] Тест HTTPS доступность..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://kkt-box.net" -TimeoutSec 10
    Write-Host "✅ HTTPS работает (код $($response.StatusCode))" -ForegroundColor Green
    Write-Host "    Content-Type: $($response.Headers['Content-Type'])" -ForegroundColor Gray
} catch {
    Write-Host "❌ HTTPS не доступен: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Тест 3: Проверка сертификата
Write-Host "[3] Информация о сертификате..." -ForegroundColor Yellow
ssh root@185.185.71.248 "certbot certificates 2>&1 | grep -A 6 'Certificate Name'"

Write-Host ""
Write-Host "=== Проверка завершена ===" -ForegroundColor Cyan
