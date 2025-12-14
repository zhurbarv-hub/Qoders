# Тест API карточки клиента на VDS
$SERVER = "http://kkt-box.net:8080"
$EMAIL = "admin@kkt.local"
$PASSWORD = "admin123"

Write-Host "=== ТЕСТ API КАРТОЧКИ КЛИЕНТА НА VDS ===" -ForegroundColor Cyan
Write-Host ""

# 1. Авторизация
Write-Host "1. Получение JWT токена..." -ForegroundColor Yellow
$loginBody = @{
    email = $EMAIL
    password = $PASSWORD
} | ConvertTo-Json

try {
    $tokenResponse = Invoke-RestMethod -Uri "$SERVER/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $TOKEN = $tokenResponse.access_token
    
    if ([string]::IsNullOrEmpty($TOKEN)) {
        Write-Host "❌ ОШИБКА: Не удалось получить токен" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✓ Токен получен: $($TOKEN.Substring(0, 20))..." -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ ОШИБКА авторизации: $_" -ForegroundColor Red
    exit 1
}

# 2. Получить список клиентов
Write-Host "2. Получение списка пользователей (клиентов)..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $TOKEN"
}

try {
    $uri = "$SERVER/api/users?role=client&page_size=10"
    $usersResponse = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
    
    Write-Host "Найдено клиентов: $($usersResponse.total)" -ForegroundColor Green
    
    if ($usersResponse.users.Count -eq 0) {
        Write-Host "❌ ОШИБКА: Не найдено ни одного клиента" -ForegroundColor Red
        exit 1
    }
    
    $USER_ID = $usersResponse.users[0].id
    Write-Host "✓ Первый клиент: ID=$USER_ID, Имя=$($usersResponse.users[0].full_name)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ ОШИБКА получения списка клиентов: $_" -ForegroundColor Red
    exit 1
}

# 3. Получить полные детали клиента
Write-Host "3. Получение полных деталей клиента ID=$USER_ID..." -ForegroundColor Yellow
try {
    $detailsResponse = Invoke-RestMethod -Uri "$SERVER/api/users/$USER_ID/full-details" -Method Get -Headers $headers
    
    Write-Host "Полный ответ (JSON):" -ForegroundColor Cyan
    $detailsResponse | ConvertTo-Json -Depth 10
    Write-Host ""
    
    # 4. Проверить наличие ключевых полей
    Write-Host "4. Проверка структуры данных..." -ForegroundColor Yellow
    
    if ($detailsResponse.PSObject.Properties['name']) {
        Write-Host "✓ Поле name найдено: $($detailsResponse.name)" -ForegroundColor Green
    } else {
        Write-Host "❌ Поле name НЕ найдено" -ForegroundColor Red
    }
    
    if ($detailsResponse.PSObject.Properties['cash_registers']) {
        Write-Host "✓ Поле cash_registers найдено: $($detailsResponse.cash_registers.Count) касс" -ForegroundColor Green
    } else {
        Write-Host "❌ Поле cash_registers НЕ найдено" -ForegroundColor Red
    }
    
    if ($detailsResponse.PSObject.Properties['register_deadlines']) {
        Write-Host "✓ Поле register_deadlines найдено: $($detailsResponse.register_deadlines.Count) дедлайнов касс" -ForegroundColor Green
    } else {
        Write-Host "❌ Поле register_deadlines НЕ найдено" -ForegroundColor Red
    }
    
    if ($detailsResponse.PSObject.Properties['general_deadlines']) {
        Write-Host "✓ Поле general_deadlines найдено: $($detailsResponse.general_deadlines.Count) общих дедлайнов" -ForegroundColor Green
    } else {
        Write-Host "❌ Поле general_deadlines НЕ найдено" -ForegroundColor Red
    }
    Write-Host ""
    
} catch {
    Write-Host "❌ ОШИБКА получения деталей клиента: $_" -ForegroundColor Red
    Write-Host "Детали ошибки: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 5. Проверить типы дедлайнов
Write-Host "5. Получение типов дедлайнов..." -ForegroundColor Yellow
try {
    $typesResponse = Invoke-RestMethod -Uri "$SERVER/api/deadline-types" -Method Get -Headers $headers
    Write-Host "Типы дедлайнов:" -ForegroundColor Cyan
    $typesResponse | ConvertTo-Json -Depth 5
    Write-Host ""
} catch {
    Write-Host "❌ ОШИБКА получения типов дедлайнов: $_" -ForegroundColor Red
}

# 6. Проверить провайдеров ОФД
Write-Host "6. Получение провайдеров ОФД..." -ForegroundColor Yellow
try {
    $ofdResponse = Invoke-RestMethod -Uri "$SERVER/api/ofd-providers" -Method Get -Headers $headers
    Write-Host "Провайдеры ОФД:" -ForegroundColor Cyan
    $ofdResponse | ConvertTo-Json -Depth 5
    Write-Host ""
} catch {
    Write-Host "❌ ОШИБКА получения провайдеров ОФД: $_" -ForegroundColor Red
}

Write-Host "=== ТЕСТ ЗАВЕРШЕН ===" -ForegroundColor Cyan
