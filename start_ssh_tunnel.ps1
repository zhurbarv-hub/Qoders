# SSH Tunnel для доступа к VDS KKT
# Пробрасывает порт 8080 с VDS на локальный 8080

$VDS_HOST = "185.185.71.248"
$VDS_USER = "root"
$LOCAL_PORT = 8080
$REMOTE_PORT = 8080

Write-Host "=== Starting SSH Tunnel to VDS ===" -ForegroundColor Cyan
Write-Host "VDS: $VDS_USER@$VDS_HOST" -ForegroundColor Yellow
Write-Host "Tunnel: localhost:$LOCAL_PORT -> VDS:$REMOTE_PORT" -ForegroundColor Yellow
Write-Host ""

# Проверка наличия SSH
try {
    $sshVersion = ssh -V 2>&1
    Write-Host "SSH found: $sshVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: SSH client not found!" -ForegroundColor Red
    Write-Host "Please install OpenSSH client:" -ForegroundColor Yellow
    Write-Host "  Windows 10/11: Settings -> Apps -> Optional Features -> OpenSSH Client" -ForegroundColor Yellow
    exit 1
}

# Проверка существующих туннелей на порту 8080
Write-Host "Checking for existing tunnels on port $LOCAL_PORT..." -ForegroundColor Yellow
$existingProcess = Get-NetTCPConnection -LocalPort $LOCAL_PORT -ErrorAction SilentlyContinue | Select-Object -First 1

if ($existingProcess) {
    Write-Host "WARNING: Port $LOCAL_PORT is already in use!" -ForegroundColor Red
    Write-Host "Process using the port:" -ForegroundColor Yellow
    Get-Process -Id $existingProcess.OwningProcess | Format-Table Name, Id, Path
    
    $response = Read-Host "Kill this process and continue? (y/n)"
    if ($response -eq 'y') {
        Stop-Process -Id $existingProcess.OwningProcess -Force
        Write-Host "Process killed." -ForegroundColor Green
        Start-Sleep -Seconds 2
    } else {
        Write-Host "Tunnel creation cancelled." -ForegroundColor Red
        exit 1
    }
}

# Создание SSH туннеля
Write-Host "`nStarting SSH tunnel..." -ForegroundColor Yellow
Write-Host "Command: ssh -L ${LOCAL_PORT}:localhost:${REMOTE_PORT} ${VDS_USER}@${VDS_HOST} -N" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tunnel will run in FOREGROUND. Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host "After tunnel is established, open browser: http://localhost:8080" -ForegroundColor Green
Write-Host ""

# Запуск туннеля (блокирующий режим)
ssh -L "${LOCAL_PORT}:localhost:${REMOTE_PORT}" "${VDS_USER}@${VDS_HOST}" -N
