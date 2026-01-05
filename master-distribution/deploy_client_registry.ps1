# ============================================
# Deploy Client Registry Database to VDS
# ============================================

$VDS_HOST = "185.185.71.248"
$VDS_USER = "root"
$VDS_PASSWORD = "7ywyrfrweitkws_bmm8k"
$DB_NAME = "kkt_master_registry"

Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "Client Registry Database Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload SQL schema to VDS
Write-Host "[1/4] Uploading schema to VDS..." -ForegroundColor Yellow
$schemaPath = Join-Path $PSScriptRoot "client_registry_schema.sql"

# Using SCP via plink (PuTTY)
if (Get-Command plink -ErrorAction SilentlyContinue) {
    Write-Host "Using plink for SSH connection..." -ForegroundColor Gray
    echo y | pscp -pw $VDS_PASSWORD $schemaPath "${VDS_USER}@${VDS_HOST}:/tmp/client_registry_schema.sql"
} else {
    Write-Host "WARNING: plink not found. Manual upload required." -ForegroundColor Red
    Write-Host "Please upload client_registry_schema.sql to VDS:/tmp/" -ForegroundColor Yellow
    Read-Host "Press Enter when uploaded"
}

# Step 2: Create database
Write-Host ""
Write-Host "[2/4] Creating database..." -ForegroundColor Yellow
$createDbCmd = "sudo -u postgres psql -c `"CREATE DATABASE $DB_NAME;`""
$grantCmd = "sudo -u postgres psql -c `"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO postgres;`""

Write-Host "Commands to execute on VDS:" -ForegroundColor Gray
Write-Host $createDbCmd -ForegroundColor White
Write-Host $grantCmd -ForegroundColor White
Write-Host ""

# Step 3: Apply schema
Write-Host "[3/4] Applying schema..." -ForegroundColor Yellow
$applySchemaCmd = "sudo -u postgres psql -d $DB_NAME -f /tmp/client_registry_schema.sql"
Write-Host "Command: $applySchemaCmd" -ForegroundColor White
Write-Host ""

# Step 4: Verify
Write-Host "[4/4] Verification commands..." -ForegroundColor Yellow
$verifyCmd = "sudo -u postgres psql -d $DB_NAME -c `"\dt`""
Write-Host "Command: $verifyCmd" -ForegroundColor White
Write-Host ""

Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "Manual Execution Required" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please SSH to VDS and execute:" -ForegroundColor White
Write-Host ""
Write-Host "ssh root@$VDS_HOST" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then run these commands:" -ForegroundColor White
Write-Host ""
Write-Host $createDbCmd -ForegroundColor Green
Write-Host $grantCmd -ForegroundColor Green
Write-Host $applySchemaCmd -ForegroundColor Green
Write-Host $verifyCmd -ForegroundColor Green
Write-Host ""
Write-Host "=================================================="  -ForegroundColor Cyan
# ============================================
# Deploy Client Registry Database to VDS
# ============================================

$VDS_HOST = "185.185.71.248"
$VDS_USER = "root"
$VDS_PASSWORD = "7ywyrfrweitkws_bmm8k"
$DB_NAME = "kkt_master_registry"

Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "Client Registry Database Deployment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upload SQL schema to VDS
Write-Host "[1/4] Uploading schema to VDS..." -ForegroundColor Yellow
$schemaPath = Join-Path $PSScriptRoot "client_registry_schema.sql"

# Using SCP via plink (PuTTY)
if (Get-Command plink -ErrorAction SilentlyContinue) {
    Write-Host "Using plink for SSH connection..." -ForegroundColor Gray
    echo y | pscp -pw $VDS_PASSWORD $schemaPath "${VDS_USER}@${VDS_HOST}:/tmp/client_registry_schema.sql"
} else {
    Write-Host "WARNING: plink not found. Manual upload required." -ForegroundColor Red
    Write-Host "Please upload client_registry_schema.sql to VDS:/tmp/" -ForegroundColor Yellow
    Read-Host "Press Enter when uploaded"
}

# Step 2: Create database
Write-Host ""
Write-Host "[2/4] Creating database..." -ForegroundColor Yellow
$createDbCmd = "sudo -u postgres psql -c `"CREATE DATABASE $DB_NAME;`""
$grantCmd = "sudo -u postgres psql -c `"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO postgres;`""

Write-Host "Commands to execute on VDS:" -ForegroundColor Gray
Write-Host $createDbCmd -ForegroundColor White
Write-Host $grantCmd -ForegroundColor White
Write-Host ""

# Step 3: Apply schema
Write-Host "[3/4] Applying schema..." -ForegroundColor Yellow
$applySchemaCmd = "sudo -u postgres psql -d $DB_NAME -f /tmp/client_registry_schema.sql"
Write-Host "Command: $applySchemaCmd" -ForegroundColor White
Write-Host ""

# Step 4: Verify
Write-Host "[4/4] Verification commands..." -ForegroundColor Yellow
$verifyCmd = "sudo -u postgres psql -d $DB_NAME -c `"\dt`""
Write-Host "Command: $verifyCmd" -ForegroundColor White
Write-Host ""

Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "Manual Execution Required" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please SSH to VDS and execute:" -ForegroundColor White
Write-Host ""
Write-Host "ssh root@$VDS_HOST" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then run these commands:" -ForegroundColor White
Write-Host ""
Write-Host $createDbCmd -ForegroundColor Green
Write-Host $grantCmd -ForegroundColor Green
Write-Host $applySchemaCmd -ForegroundColor Green
Write-Host $verifyCmd -ForegroundColor Green
Write-Host ""
Write-Host "=================================================="  -ForegroundColor Cyan
