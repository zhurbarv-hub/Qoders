# ============================================
# Deploy Client Registry to kkt-box.net
# Развертывание Client Registry Database
# ============================================

param(
    [string]$VDSHost = "185.185.71.248",
    [string]$VDSUser = "root",
    [string]$VDSPassword = "7ywyrfrweitkws_bmm8k"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deploy Client Registry Database" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Пути
$LocalPath = "$PSScriptRoot"
$RemotePath = "/tmp/kkt-master-setup"

Write-Host "Локальный путь: $LocalPath" -ForegroundColor Gray
Write-Host "VDS: $VDSHost" -ForegroundColor Gray
Write-Host ""

# ============================================
# Шаг 1: Создание временной директории на VDS
# ============================================
Write-Host "[1/5] Создание временной директории на VDS..." -ForegroundColor Yellow

$sshCommand = "mkdir -p $RemotePath"
$result = plink -batch -pw $VDSPassword ${VDSUser}@${VDSHost} $sshCommand 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Ошибка создания директории" -ForegroundColor Red
    Write-Host $result
    exit 1
}

Write-Host "✓ Директория создана" -ForegroundColor Green

# ============================================
# Шаг 2: Копирование файлов
# ============================================
Write-Host "[2/5] Копирование файлов на VDS..." -ForegroundColor Yellow

# SQL схема
Write-Host "  - client_registry_schema.sql" -ForegroundColor Gray
pscp -batch -pw $VDSPassword "$LocalPath\client_registry_schema.sql" "${VDSUser}@${VDSHost}:${RemotePath}/"

# Setup скрипт
Write-Host "  - setup_client_registry.sh" -ForegroundColor Gray
pscp -batch -pw $VDSPassword "$LocalPath\setup_client_registry.sh" "${VDSUser}@${VDSHost}:${RemotePath}/"

Write-Host "✓ Файлы скопированы" -ForegroundColor Green

# ============================================
# Шаг 3: Установка прав на выполнение
# ============================================
Write-Host "[3/5] Установка прав на выполнение..." -ForegroundColor Yellow

$sshCommand = "chmod +x $RemotePath/*.sh"
plink -batch -pw $VDSPassword ${VDSUser}@${VDSHost} $sshCommand

Write-Host "✓ Права установлены" -ForegroundColor Green

# ============================================
# Шаг 4: Выполнение setup скрипта
# ============================================
Write-Host "[4/5] Запуск setup скрипта..." -ForegroundColor Yellow
Write-Host ""

$sshCommand = "cd $RemotePath; ./setup_client_registry.sh"
plink -batch -pw $VDSPassword ${VDSUser}@${VDSHost} $sshCommand

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Ошибка при выполнении setup" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Setup выполнен успешно" -ForegroundColor Green

# ============================================
# Шаг 5: Очистка временных файлов
# ============================================
Write-Host "[5/5] Очистка временных файлов..." -ForegroundColor Yellow

$sshCommand = "rm -rf $RemotePath"
plink -batch -pw $VDSPassword ${VDSUser}@${VDSHost} $sshCommand

Write-Host "✓ Временные файлы удалены" -ForegroundColor Green

# ============================================
# Итоговая информация
# ============================================
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Client Registry Database установлена!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Информация о БД:" -ForegroundColor White
Write-Host "  Имя: kkt_master_registry" -ForegroundColor Gray
Write-Host "  Пользователь: kkt_user" -ForegroundColor Gray
Write-Host "  Суперадмин: admin@kkt-master.local / admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "Проверка БД:" -ForegroundColor White
Write-Host "  ssh root@$VDSHost" -ForegroundColor Gray
Write-Host "  sudo -u postgres psql -d kkt_master_registry" -ForegroundColor Gray
Write-Host ""
