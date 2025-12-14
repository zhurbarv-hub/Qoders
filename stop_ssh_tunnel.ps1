# Остановка SSH туннеля
# Убивает все SSH процессы, связанные с форвардингом порта 8080

$LOCAL_PORT = 8080

Write-Host "=== Stopping SSH Tunnel ===" -ForegroundColor Cyan
Write-Host "Searching for processes using port $LOCAL_PORT..." -ForegroundColor Yellow

# Найти процесс на порту 8080
$connections = Get-NetTCPConnection -LocalPort $LOCAL_PORT -ErrorAction SilentlyContinue

if ($connections) {
    $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    
    foreach ($pid in $processIds) {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Found process: $($process.Name) (PID: $pid)" -ForegroundColor Yellow
            
            try {
                Stop-Process -Id $pid -Force
                Write-Host "Process $pid stopped." -ForegroundColor Green
            } catch {
                Write-Host "ERROR: Failed to stop process $pid" -ForegroundColor Red
                Write-Host $_.Exception.Message -ForegroundColor Red
            }
        }
    }
    
    Write-Host "`nSSH tunnel stopped successfully!" -ForegroundColor Green
} else {
    Write-Host "No active SSH tunnel found on port $LOCAL_PORT" -ForegroundColor Yellow
}

# Также попробуем убить все SSH процессы (опционально)
Write-Host "`nSearching for SSH processes..." -ForegroundColor Yellow
$sshProcesses = Get-Process -Name ssh -ErrorAction SilentlyContinue

if ($sshProcesses) {
    Write-Host "Found $($sshProcesses.Count) SSH process(es):" -ForegroundColor Yellow
    $sshProcesses | Format-Table Id, Name, StartTime
    
    $response = Read-Host "Kill all SSH processes? (y/n)"
    if ($response -eq 'y') {
        $sshProcesses | ForEach-Object {
            Stop-Process -Id $_.Id -Force
            Write-Host "Killed SSH process PID $($_.Id)" -ForegroundColor Green
        }
    }
} else {
    Write-Host "No SSH processes found." -ForegroundColor Yellow
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
