$SERVER = "http://kkt-box.net:8080"
$EMAIL = "admin@kkt.local"
$PASSWORD = "admin123"

Write-Host "=== TEST CLIENT CARD API ON VDS ===" -ForegroundColor Cyan

# 1. Login
Write-Host "`n1. Getting JWT token..." -ForegroundColor Yellow
$loginBody = @{ email = $EMAIL; password = $PASSWORD } | ConvertTo-Json

$tokenResponse = Invoke-RestMethod -Uri "$SERVER/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
$TOKEN = $tokenResponse.access_token
Write-Host "Token received: $($TOKEN.Substring(0, 20))..." -ForegroundColor Green

# 2. Get clients list
Write-Host "`n2. Getting clients list..." -ForegroundColor Yellow
$headers = @{ "Authorization" = "Bearer $TOKEN" }

$uri1 = $SERVER + "/api/users"
$usersResponse = Invoke-RestMethod -Uri $uri1 -Method Get -Headers $headers -Body @{ role = "client"; page_size = 10 }

Write-Host "Found clients: $($usersResponse.total)" -ForegroundColor Green
$USER_ID = $usersResponse.users[0].id
Write-Host "First client: ID=$USER_ID, Name=$($usersResponse.users[0].full_name)" -ForegroundColor Green

# 3. Get full client details
Write-Host "`n3. Getting full client details for ID=$USER_ID..." -ForegroundColor Yellow
$uri2 = "$SERVER/api/users/$USER_ID/full-details"
$detailsResponse = Invoke-RestMethod -Uri $uri2 -Method Get -Headers $headers

Write-Host "`nFull response:" -ForegroundColor Cyan
$detailsResponse | ConvertTo-Json -Depth 10

# 4. Check fields
Write-Host "`n4. Field validation:" -ForegroundColor Yellow
if ($detailsResponse.name) { Write-Host "OK: name = $($detailsResponse.name)" -ForegroundColor Green }
if ($detailsResponse.cash_registers) { Write-Host "OK: cash_registers count = $($detailsResponse.cash_registers.Count)" -ForegroundColor Green }
if ($detailsResponse.register_deadlines) { Write-Host "OK: register_deadlines count = $($detailsResponse.register_deadlines.Count)" -ForegroundColor Green }
if ($detailsResponse.general_deadlines) { Write-Host "OK: general_deadlines count = $($detailsResponse.general_deadlines.Count)" -ForegroundColor Green }

# 5. Get deadline types
Write-Host "`n5. Getting deadline types..." -ForegroundColor Yellow
$uri3 = "$SERVER/api/deadline-types"
$typesResponse = Invoke-RestMethod -Uri $uri3 -Method Get -Headers $headers
Write-Host "Deadline types: $($typesResponse.deadline_types.Count)" -ForegroundColor Green

# 6. Get OFD providers
Write-Host "`n6. Getting OFD providers..." -ForegroundColor Yellow
$uri4 = "$SERVER/api/ofd-providers"
$ofdResponse = Invoke-RestMethod -Uri $uri4 -Method Get -Headers $headers
Write-Host "OFD providers: $($ofdResponse.providers.Count)" -ForegroundColor Green

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Cyan
