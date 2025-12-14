$SERVER = "http://kkt-box.net:8080"
$EMAIL = "admin@kkt-system.local"
$PASSWORD = "admin123"

Write-Host "=== Test OFD and Cash Register APIs ===" -ForegroundColor Cyan

# 1. Login
Write-Host "`n1. Login..." -ForegroundColor Yellow
$loginBody = @{
    username = $EMAIL
    password = $PASSWORD
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "$SERVER/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $response.access_token
    Write-Host "OK: Logged in successfully" -ForegroundColor Green
} catch {
    Write-Host "FAIL: Login failed" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
}

# 2. Test OFD Providers
Write-Host "`n2. Test OFD Providers API..." -ForegroundColor Yellow
try {
    $ofdProviders = Invoke-RestMethod -Uri "$SERVER/api/ofd-providers" -Method Get -Headers $headers
    Write-Host "OK: OFD Providers loaded: $($ofdProviders.Count) providers" -ForegroundColor Green
    if ($ofdProviders.Count -gt 0) {
        Write-Host "  First provider: $($ofdProviders[0].name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "FAIL: OFD Providers failed - $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Test Cash Register Creation
Write-Host "`n3. Test Cash Register Creation..." -ForegroundColor Yellow
$testRegister = @{
    client_id = 4
    factory_number = "TEST-001"
    registration_number = "REG-001"
    model = "Atol 91F"
    fn_number = "FN-12345"
    ofd_provider_id = 1
    notes = "Test register"
} | ConvertTo-Json -Compress

Write-Host "Sending JSON: $testRegister" -ForegroundColor Gray

try {
    $newRegister = Invoke-RestMethod -Uri "$SERVER/api/cash-registers" -Method Post -Body $testRegister -ContentType "application/json; charset=utf-8" -Headers $headers
    Write-Host "OK: Cash Register created successfully" -ForegroundColor Green
    Write-Host "  ID: $($newRegister.id), Model: $($newRegister.model)" -ForegroundColor Gray
} catch {
    Write-Host "FAIL: Cash Register creation failed" -ForegroundColor Red
    Write-Host "  Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        try {
            $errorDetail = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "  Error: $($errorDetail.detail)" -ForegroundColor Red
        } catch {
            Write-Host "  Raw Error: $($_.ErrorDetails.Message)" -ForegroundColor Red
        }
    }
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
