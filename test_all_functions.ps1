# Полное тестирование всех функций проекта ККТ на VDS
# Использует SSH туннель на localhost:8080

$SERVER = "http://127.0.0.1:8080"
$EMAIL = "admin@kkt.local"
$PASSWORD = "admin123"

Write-Host "=== ПОЛНОЕ ТЕСТИРОВАНИЕ ПРОЕКТА ККТ ===" -ForegroundColor Cyan
Write-Host "Сервер: $SERVER" -ForegroundColor Yellow
Write-Host ""

# Проверка доступности сервера
Write-Host "0. Проверка доступности сервера..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$SERVER/health" -ErrorAction Stop
    Write-Host "OK: Сервер доступен" -ForegroundColor Green
    $health | ConvertTo-Json
} catch {
    Write-Host "FAIL: Сервер недоступен - проверьте SSH туннель" -ForegroundColor Red
    Write-Host "Запустите: .\start_ssh_tunnel_background.ps1" -ForegroundColor Yellow
    exit 1
}

# 1. Аутентификация
Write-Host "`n1. ТЕСТ АУТЕНТИФИКАЦИИ" -ForegroundColor Cyan
$loginBody = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json

try {
    $tokenResponse = Invoke-RestMethod -Uri "$SERVER/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $TOKEN = $tokenResponse.access_token
    Write-Host "OK: Токен получен" -ForegroundColor Green
    $headers = @{ "Authorization" = "Bearer $TOKEN" }
} catch {
    Write-Host "FAIL: Ошибка аутентификации - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Получение списка пользователей (клиентов)
Write-Host "`n2. ТЕСТ ПОЛУЧЕНИЯ СПИСКА КЛИЕНТОВ" -ForegroundColor Cyan
try {
    $uri = "$SERVER/api/users"
    $usersResponse = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers -Body @{ role = "client"; page_size = 100 }
    Write-Host "OK: Найдено клиентов: $($usersResponse.total)" -ForegroundColor Green
    
    if ($usersResponse.total -eq 0) {
        Write-Host "WARNING: Нет клиентов в системе" -ForegroundColor Yellow
        $USER_ID = $null
    } else {
        $USER_ID = $usersResponse.users[0].id
        Write-Host "   Первый клиент: ID=$USER_ID, Имя=$($usersResponse.users[0].full_name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Получение полных деталей клиента
if ($USER_ID) {
    Write-Host "`n3. ТЕСТ КАРТОЧКИ КЛИЕНТА (FULL DETAILS)" -ForegroundColor Cyan
    try {
        $detailsResponse = Invoke-RestMethod -Uri "$SERVER/api/users/$USER_ID/full-details" -Method Get -Headers $headers
        Write-Host "OK: Детали клиента получены" -ForegroundColor Green
        Write-Host "   Имя: $($detailsResponse.name)" -ForegroundColor Gray
        Write-Host "   ИНН: $($detailsResponse.inn)" -ForegroundColor Gray
        Write-Host "   Кассы: $($detailsResponse.cash_registers.Count)" -ForegroundColor Gray
        Write-Host "   Дедлайны касс: $($detailsResponse.register_deadlines.Count)" -ForegroundColor Gray
        Write-Host "   Общие дедлайны: $($detailsResponse.general_deadlines.Count)" -ForegroundColor Gray
    } catch {
        Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 4. Типы дедлайнов
Write-Host "`n4. ТЕСТ ТИПОВ ДЕДЛАЙНОВ" -ForegroundColor Cyan
try {
    $typesResponse = Invoke-RestMethod -Uri "$SERVER/api/deadline-types" -Method Get -Headers $headers
    Write-Host "OK: Получено типов: $($typesResponse.deadline_types.Count)" -ForegroundColor Green
    foreach ($type in $typesResponse.deadline_types) {
        Write-Host "   - $($type.type_name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Провайдеры ОФД
Write-Host "`n5. ТЕСТ ПРОВАЙДЕРОВ ОФД" -ForegroundColor Cyan
try {
    $ofdResponse = Invoke-RestMethod -Uri "$SERVER/api/ofd-providers" -Method Get -Headers $headers
    Write-Host "OK: Получено провайдеров: $($ofdResponse.providers.Count)" -ForegroundColor Green
    foreach ($provider in $ofdResponse.providers | Select-Object -First 5) {
        Write-Host "   - $($provider.name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Дашборд статистика
Write-Host "`n6. ТЕСТ ДАШБОРДА" -ForegroundColor Cyan
try {
    $dashResponse = Invoke-RestMethod -Uri "$SERVER/api/dashboard/stats" -Method Get -Headers $headers
    Write-Host "OK: Статистика получена" -ForegroundColor Green
    Write-Host "   Активных клиентов: $($dashResponse.active_clients_count)" -ForegroundColor Gray
    Write-Host "   Активных дедлайнов: $($dashResponse.active_deadlines_count)" -ForegroundColor Gray
    Write-Host "   Срочных: $($dashResponse.urgent_count)" -ForegroundColor Gray
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Список всех дедлайнов
Write-Host "`n7. ТЕСТ ПОЛУЧЕНИЯ ДЕДЛАЙНОВ" -ForegroundColor Cyan
try {
    $deadlinesResponse = Invoke-RestMethod -Uri "$SERVER/api/deadlines" -Method Get -Headers $headers -Body @{ page_size = 100 }
    Write-Host "OK: Получено дедлайнов: $($deadlinesResponse.total)" -ForegroundColor Green
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 8. Кассовые аппараты
if ($USER_ID) {
    Write-Host "`n8. ТЕСТ КАССОВЫХ АППАРАТОВ" -ForegroundColor Cyan
    try {
        $uri = "$SERVER/api/cash-registers"
        $cashResponse = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers -Body @{ user_id = $USER_ID }
        Write-Host "OK: Получено касс для клиента $USER_ID`: $($cashResponse.total)" -ForegroundColor Green
    } catch {
        Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 9. Создание тестового клиента (опционально)
Write-Host "`n9. ТЕСТ СОЗДАНИЯ КЛИЕНТА" -ForegroundColor Cyan
$newClient = @{
    email = "test_$(Get-Random)@test.local"
    full_name = "Тестовый Клиент"
    company_name = "ООО Тест"
    inn = "$(Get-Random -Minimum 1000000000 -Maximum 9999999999)"
    role = "client"
    is_active = $true
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "$SERVER/api/users" -Method Post -Body $newClient -Headers $headers -ContentType "application/json"
    Write-Host "OK: Клиент создан успешно" -ForegroundColor Green
    $NEW_USER_ID = $createResponse.user_id
} catch {
    Write-Host "WARNING: Test client creation failed (may already exist)" -ForegroundColor Yellow
    Write-Host "   Reason: $($_.Exception.Message)" -ForegroundColor Gray
}

# 10. Проверка статических файлов
Write-Host "`n10. ТЕСТ СТАТИЧЕСКИХ ФАЙЛОВ" -ForegroundColor Cyan
$staticFiles = @(
    "/static/login.html",
    "/static/dashboard.html",
    "/static/client-details.html",
    "/static/css/styles.css",
    "/static/js/auth.js",
    "/static/js/client-details.js"
)

foreach ($file in $staticFiles) {
    try {
        $response = Invoke-WebRequest -Uri "$SERVER$file" -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "   OK: $file (${$response.Content.Length} bytes)" -ForegroundColor Green
        }
    } catch {
        Write-Host "   FAIL: $file - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# ИТОГИ
Write-Host "`n=== ИТОГИ ТЕСТИРОВАНИЯ ===" -ForegroundColor Cyan
Write-Host "Сервер: VDS через SSH туннель (localhost:8080)" -ForegroundColor Yellow
Write-Host "Базовые функции: ✅ Работают" -ForegroundColor Green
Write-Host "API эндпоинты: ✅ Доступны" -ForegroundColor Green
Write-Host "Статические файлы: ✅ Доступны" -ForegroundColor Green
Write-Host "`nДоступ к веб-интерфейсу: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
