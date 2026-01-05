$loginBody = '{"username":"eliseev","password":"eliseev"}'
$loginResponse = Invoke-RestMethod -Uri "http://185.185.71.248:8080/api/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
$token = $loginResponse.access_token

$headers = @{ "Authorization" = "Bearer $token" }
$stats = Invoke-RestMethod -Uri "http://185.185.71.248:8080/api/dashboard/stats" -Method Get -Headers $headers

Write-Host "Total cash registers: $($stats.total_cash_registers)"
