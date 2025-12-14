$SERVER = "http://kkt-box.net:8080"
$EMAIL = "admin@kkt-system.local"
$PASSWORD = "admin123"

Write-Host "=== DEBUG CLIENT CARD ON VDS ===" -ForegroundColor Cyan

# 1. Login
Write-Host "`n1. Login..." -ForegroundColor Yellow
$loginBody = @{
    username = $EMAIL
    password = $PASSWORD
} | ConvertTo-Json -Compress

Write-Host "Login body: $loginBody" -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri "$SERVER/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json" -UseBasicParsing
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor Gray
    
    $tokenData = $response.Content | ConvertFrom-Json
    $TOKEN = $tokenData.access_token
    Write-Host "Token: $($TOKEN.Substring(0,20))..." -ForegroundColor Green
    $headers = @{ "Authorization" = "Bearer $TOKEN" }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Error details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit 1
}

# 2. Get users list
Write-Host "`n2. Get users (clients)..." -ForegroundColor Yellow
try {
    $usersUri = "$SERVER/api/users?role=client&page_size=10"
    Write-Host "URI: $usersUri" -ForegroundColor Gray
    
    $usersResponse = Invoke-RestMethod -Uri $usersUri -Method Get -Headers $headers
    Write-Host "Total clients: $($usersResponse.total)" -ForegroundColor Green
    
    if ($usersResponse.total -eq 0) {
        Write-Host "No clients found!" -ForegroundColor Red
        exit 1
    }
    
    $USER_ID = $usersResponse.users[0].id
    Write-Host "First client:" -ForegroundColor Green
    Write-Host "  ID: $USER_ID" -ForegroundColor Gray
    Write-Host "  Name: $($usersResponse.users[0].full_name)" -ForegroundColor Gray
    Write-Host "  Email: $($usersResponse.users[0].email)" -ForegroundColor Gray
    Write-Host "  INN: $($usersResponse.users[0].inn)" -ForegroundColor Gray
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 3. Get client full details
Write-Host "`n3. Get client full details (ID=$USER_ID)..." -ForegroundColor Yellow
try {
    $detailsUri = "$SERVER/api/users/$USER_ID/full-details"
    Write-Host "URI: $detailsUri" -ForegroundColor Gray
    
    $detailsResponse = Invoke-RestMethod -Uri $detailsUri -Method Get -Headers $headers
    
    Write-Host "SUCCESS: Client details loaded" -ForegroundColor Green
    Write-Host "`nClient Info:" -ForegroundColor Cyan
    Write-Host "  ID: $($detailsResponse.id)" -ForegroundColor Gray
    Write-Host "  Name: $($detailsResponse.name)" -ForegroundColor Gray
    Write-Host "  INN: $($detailsResponse.inn)" -ForegroundColor Gray
    Write-Host "  Email: $($detailsResponse.email)" -ForegroundColor Gray
    Write-Host "  Phone: $($detailsResponse.phone)" -ForegroundColor Gray
    Write-Host "  Address: $($detailsResponse.address)" -ForegroundColor Gray
    Write-Host "  Telegram ID: $($detailsResponse.telegram_id)" -ForegroundColor Gray
    
    Write-Host "`nCash Registers: $($detailsResponse.cash_registers.Count)" -ForegroundColor Cyan
    foreach ($reg in $detailsResponse.cash_registers) {
        Write-Host "  - ID: $($reg.id), Name: $($reg.register_name), Serial: $($reg.serial_number)" -ForegroundColor Gray
    }
    
    Write-Host "`nRegister Deadlines: $($detailsResponse.register_deadlines.Count)" -ForegroundColor Cyan
    foreach ($deadline in $detailsResponse.register_deadlines) {
        Write-Host "  - Type: $($deadline.deadline_type_name), Date: $($deadline.expiration_date), Days: $($deadline.days_until_expiration)" -ForegroundColor Gray
    }
    
    Write-Host "`nGeneral Deadlines: $($detailsResponse.general_deadlines.Count)" -ForegroundColor Cyan
    foreach ($deadline in $detailsResponse.general_deadlines) {
        Write-Host "  - Type: $($deadline.deadline_type_name), Date: $($deadline.expiration_date), Days: $($deadline.days_until_expiration)" -ForegroundColor Gray
    }
    
    Write-Host "`nFull JSON Response:" -ForegroundColor Cyan
    $detailsResponse | ConvertTo-Json -Depth 10
    
} catch {
    Write-Host "FAIL: Cannot load client details" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    
    # Check VDS logs
    Write-Host "`nChecking VDS logs..." -ForegroundColor Yellow
    ssh root@185.185.71.248 "journalctl -u kkt-web -n 30 --no-pager"
    exit 1
}

Write-Host "`n=== DEBUG COMPLETE ===" -ForegroundColor Green
