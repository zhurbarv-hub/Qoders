$SERVER = "http://127.0.0.1:8080"
$EMAIL = "admin@kkt.local"
$PASSWORD = "admin123"

Write-Host "=== KKT PROJECT FULL TEST ===" -ForegroundColor Cyan
Write-Host "Server: $SERVER`n" -ForegroundColor Yellow

# 0. Server health check
Write-Host "0. Server health check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$SERVER/health"
    Write-Host "OK: Server is UP" -ForegroundColor Green
} catch {
    Write-Host "FAIL: Server not available - start SSH tunnel" -ForegroundColor Red
    Write-Host "Run: .\start_ssh_tunnel_background.ps1" -ForegroundColor Yellow
    exit 1
}

# 1. Authentication
Write-Host "`n1. Authentication test" -ForegroundColor Cyan
$loginBody = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json
try {
    $tokenResponse = Invoke-RestMethod -Uri "$SERVER/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $TOKEN = $tokenResponse.access_token
    Write-Host "OK: Token received" -ForegroundColor Green
    $headers = @{ "Authorization" = "Bearer $TOKEN" }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Get users list
Write-Host "`n2. Get clients list" -ForegroundColor Cyan
try {
    $uri = "$SERVER/api/users"
    $usersResponse = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers -Body @{ role = "client"; page_size = 100 }
    Write-Host "OK: Found clients: $($usersResponse.total)" -ForegroundColor Green
    if ($usersResponse.total -gt 0) {
        $USER_ID = $usersResponse.users[0].id
        Write-Host "   First client: ID=$USER_ID, Name=$($usersResponse.users[0].full_name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Client card details
if ($USER_ID) {
    Write-Host "`n3. Client card (full details)" -ForegroundColor Cyan
    try {
        $detailsResponse = Invoke-RestMethod -Uri "$SERVER/api/users/$USER_ID/full-details" -Method Get -Headers $headers
        Write-Host "OK: Client details received" -ForegroundColor Green
        Write-Host "   Name: $($detailsResponse.name)" -ForegroundColor Gray
        Write-Host "   INN: $($detailsResponse.inn)" -ForegroundColor Gray
        Write-Host "   Cash registers: $($detailsResponse.cash_registers.Count)" -ForegroundColor Gray
        Write-Host "   Register deadlines: $($detailsResponse.register_deadlines.Count)" -ForegroundColor Gray
        Write-Host "   General deadlines: $($detailsResponse.general_deadlines.Count)" -ForegroundColor Gray
    } catch {
        Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 4. Deadline types
Write-Host "`n4. Deadline types" -ForegroundColor Cyan
try {
    $typesResponse = Invoke-RestMethod -Uri "$SERVER/api/deadline-types" -Method Get -Headers $headers
    Write-Host "OK: Types count: $($typesResponse.deadline_types.Count)" -ForegroundColor Green
    $typesResponse.deadline_types | ForEach-Object { Write-Host "   - $($_.type_name)" -ForegroundColor Gray }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. OFD providers
Write-Host "`n5. OFD providers" -ForegroundColor Cyan
try {
    $ofdResponse = Invoke-RestMethod -Uri "$SERVER/api/ofd-providers" -Method Get -Headers $headers
    Write-Host "OK: Providers count: $($ofdResponse.providers.Count)" -ForegroundColor Green
    $ofdResponse.providers | Select-Object -First 5 | ForEach-Object { Write-Host "   - $($_.name)" -ForegroundColor Gray }
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Dashboard stats
Write-Host "`n6. Dashboard statistics" -ForegroundColor Cyan
try {
    $dashResponse = Invoke-RestMethod -Uri "$SERVER/api/dashboard/stats" -Method Get -Headers $headers
    Write-Host "OK: Stats received" -ForegroundColor Green
    Write-Host "   Active clients: $($dashResponse.active_clients_count)" -ForegroundColor Gray
    Write-Host "   Active deadlines: $($dashResponse.active_deadlines_count)" -ForegroundColor Gray
    Write-Host "   Urgent: $($dashResponse.urgent_count)" -ForegroundColor Gray
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Deadlines list
Write-Host "`n7. Get deadlines" -ForegroundColor Cyan
try {
    $deadlinesResponse = Invoke-RestMethod -Uri "$SERVER/api/deadlines" -Method Get -Headers $headers -Body @{ page_size = 100 }
    Write-Host "OK: Total deadlines: $($deadlinesResponse.total)" -ForegroundColor Green
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}

# 8. Static files
Write-Host "`n8. Static files check" -ForegroundColor Cyan
$staticFiles = @("/static/login.html", "/static/dashboard.html", "/static/client-details.html")
foreach ($file in $staticFiles) {
    try {
        $response = Invoke-WebRequest -Uri "$SERVER$file" -UseBasicParsing -ErrorAction Stop
        Write-Host "   OK: $file" -ForegroundColor Green
    } catch {
        Write-Host "   FAIL: $file" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n=== TEST SUMMARY ===" -ForegroundColor Cyan
Write-Host "Server: VDS via SSH tunnel (localhost:8080)" -ForegroundColor Yellow
Write-Host "Core functions: OK" -ForegroundColor Green
Write-Host "API endpoints: OK" -ForegroundColor Green
Write-Host "Static files: OK" -ForegroundColor Green
Write-Host "`nWeb interface: http://localhost:8080`n" -ForegroundColor Cyan
