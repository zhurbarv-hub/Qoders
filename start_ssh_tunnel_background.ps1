# SSH Tunnel для доступа к VDS KKT (фоновый режим)
# Запускается в отдельном окне PowerShell

$VDS_HOST = "185.185.71.248"
$VDS_USER = "root"
$LOCAL_PORT = 8080
$REMOTE_PORT = 8080

Write-Host "=== Starting SSH Tunnel to VDS (Background) ===" -ForegroundColor Cyan
Write-Host "VDS: $VDS_USER@$VDS_HOST" -ForegroundColor Yellow
Write-Host "Tunnel: localhost:$LOCAL_PORT -> VDS:$REMOTE_PORT" -ForegroundColor Yellow
Write-Host ""

# Проверка наличия SSH
try {
    $sshVersion = ssh -V 2>&1
    Write-Host "SSH found: $sshVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: SSH client not found!" -ForegroundColor Red
    exit 1
}

# Проверка существующих туннелей
$existingProcess = Get-NetTCPConnection -LocalPort $LOCAL_PORT -ErrorAction SilentlyContinue | Select-Object -First 1

if ($existingProcess) {
    Write-Host "WARNING: Port $LOCAL_PORT is already in use!" -ForegroundColor Red
    $proc = Get-Process -Id $existingProcess.OwningProcess
    Write-Host "Process: $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Yellow
    
    $response = Read-Host "Kill this process? (y/n)"
    if ($response -eq 'y') {
        Stop-Process -Id $existingProcess.OwningProcess -Force
        Write-Host "Process killed." -ForegroundColor Green
        Start-Sleep -Seconds 2
    } else {
        exit 1
    }
}

# Запуск туннеля в новом окне
Write-Host "`nStarting SSH tunnel in new window..." -ForegroundColor Yellow
$command = "ssh -L ${LOCAL_PORT}:localhost:${REMOTE_PORT} ${VDS_USER}@${VDS_HOST} -N"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $command -WindowStyle Normal

Write-Host "SSH tunnel started in new window!" -ForegroundColor Green
Write-Host "Access the application at: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop the tunnel, close the SSH window or run: .\stop_ssh_tunnel.ps1" -ForegroundColor Yellow
