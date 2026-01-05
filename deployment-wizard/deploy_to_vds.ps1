# Deploy Deployment Wizard to VDS
$VDS_IP = "185.185.71.248"
$ROOT_PASSWORD = "7ywyrfrweitkws_bmm8k"
$REMOTE_PATH = "/opt/kkt-deployment-wizard"

Write-Host "Deploying Deployment Wizard to VDS..." -ForegroundColor Green

# Create remote directory
Write-Host "Creating remote directory..."
plink -batch -pw $ROOT_PASSWORD root@$VDS_IP "mkdir -p $REMOTE_PATH"

# Upload files
Write-Host "Uploading backend files..."
pscp -batch -pw $ROOT_PASSWORD -r backend root@${VDS_IP}:$REMOTE_PATH/
pscp -batch -pw $ROOT_PASSWORD requirements.txt root@${VDS_IP}:$REMOTE_PATH/
pscp -batch -pw $ROOT_PASSWORD .env.example root@${VDS_IP}:$REMOTE_PATH/

# Setup on VDS
$setupScript = @"
cd $REMOTE_PATH
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env from example
cp .env.example .env
echo 'DATABASE_URL=postgresql://kkt_user:PASSWORD@localhost/kkt_master_registry' > .env
echo 'GITHUB_REPO=zhurbarv-hub/Qoders' >> .env
echo 'MASTER_DOMAIN=kkt-box.net' >> .env

# Create systemd service
cat > /tmp/kkt-deployment-wizard.service <<'EOF'
[Unit]
Description=KKT Deployment Wizard
After=network.target postgresql.service

[Service]
Type=simple
User=kktapp
WorkingDirectory=$REMOTE_PATH
Environment=PATH=$REMOTE_PATH/venv/bin
EnvironmentFile=$REMOTE_PATH/.env
ExecStart=$REMOTE_PATH/venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8100
Restart=always

[Install]
WantedBy=multi-user.target
EOF

mv /tmp/kkt-deployment-wizard.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable kkt-deployment-wizard
systemctl start kkt-deployment-wizard

echo 'Deployment Wizard installed and started'
"@

Write-Host "Running setup on VDS..."
$setupScript | plink -batch -pw $ROOT_PASSWORD root@$VDS_IP

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Service running on: http://kkt-box.net:8100"
Write-Host "Check status: systemctl status kkt-deployment-wizard"
