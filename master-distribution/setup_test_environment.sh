#!/bin/bash
# ============================================
# Setup Test Environment on Production VDS
# Creates isolated test copy of production
# ============================================

set -e

echo "=================================================="
echo "Test Environment Setup"
echo "=================================================="

# Configuration
TEST_DB="kkt_test_instance"
TEST_PORT="8200"
TEST_DIR="/home/kktapp/kkt-test-system"
PROD_DIR="/home/kktapp/kkt-system"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}WARNING: This will create test environment on PRODUCTION VDS${NC}"
echo -e "${YELLOW}Make sure you have test Telegram bot token ready!${NC}"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Create test database
echo ""
echo -e "${YELLOW}[1/7] Creating test database...${NC}"
sudo -u postgres psql -c "CREATE DATABASE $TEST_DB;" 2>/dev/null || echo "DB already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $TEST_DB TO kkt_user;"
echo -e "${GREEN}✓ Test database created${NC}"

# Step 2: Copy production schema
echo ""
echo -e "${YELLOW}[2/7] Copying production schema...${NC}"
sudo -u postgres pg_dump -s kkt_production | sudo -u postgres psql -d $TEST_DB
echo -e "${GREEN}✓ Schema copied${NC}"

# Step 3: Create test application directory
echo ""
echo -e "${YELLOW}[3/7] Creating test application directory...${NC}"
if [ -d "$TEST_DIR" ]; then
    echo "Test directory exists, backing up..."
    mv $TEST_DIR ${TEST_DIR}.backup.$(date +%Y%m%d_%H%M%S)
fi

sudo -u kktapp cp -r $PROD_DIR $TEST_DIR
echo -e "${GREEN}✓ Test directory created${NC}"

# Step 4: Configure test .env
echo ""
echo -e "${YELLOW}[4/7] Configuring test .env...${NC}"

cat > /tmp/test_env_updates <<'EOF'
# Test environment configuration
DATABASE_URL=postgresql://kkt_user:PASSWORD@localhost/$TEST_DB
API_PORT=$TEST_PORT
WEB_API_BASE_URL=http://localhost:$TEST_PORT
TELEGRAM_BOT_TOKEN=TEST_BOT_TOKEN_HERE
EOF

# Copy production env and modify for test
sudo -u kktapp cp $PROD_DIR/.env $TEST_DIR/.env
# Note: Manual edit required for bot token
echo -e "${YELLOW}⚠ MANUAL STEP REQUIRED: Edit $TEST_DIR/.env${NC}"
echo -e "${YELLOW}   - Update TELEGRAM_BOT_TOKEN with test bot token${NC}"
echo -e "${YELLOW}   - Update DATABASE_URL database name to $TEST_DB${NC}"
echo -e "${YELLOW}   - Update API_PORT to $TEST_PORT${NC}"

# Step 5: Create test systemd services
echo ""
echo -e "${YELLOW}[5/7] Creating test systemd services...${NC}"

# Test web service
cat > /tmp/kkt-test-web.service <<EOF
[Unit]
Description=KKT Test Web Application
After=network.target postgresql.service

[Service]
Type=simple
User=kktapp
WorkingDirectory=$TEST_DIR
Environment="PATH=$TEST_DIR/venv/bin"
EnvironmentFile=$TEST_DIR/.env
ExecStart=$TEST_DIR/venv/bin/uvicorn web.app.main:app --host 127.0.0.1 --port $TEST_PORT
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/kkt-test-web.service /etc/systemd/system/

# Test bot service  
cat > /tmp/kkt-test-bot.service <<EOF
[Unit]
Description=KKT Test Telegram Bot
After=network.target kkt-test-web.service

[Service]
Type=simple
User=kktapp
WorkingDirectory=$TEST_DIR
Environment="PATH=$TEST_DIR/venv/bin"
EnvironmentFile=$TEST_DIR/.env
ExecStart=$TEST_DIR/venv/bin/python bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/kkt-test-bot.service /etc/systemd/system/

sudo systemctl daemon-reload
echo -e "${GREEN}✓ Test services created${NC}"

# Step 6: Configure Nginx for test
echo ""
echo -e "${YELLOW}[6/7] Configuring Nginx for test path...${NC}"

cat > /tmp/nginx_test_location <<'EOF'
    # Test environment
    location /test/ {
        proxy_pass http://127.0.0.1:8200/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
EOF

echo -e "${YELLOW}⚠ MANUAL STEP: Add above location to Nginx config${NC}"
echo -e "${YELLOW}   File: /etc/nginx/sites-available/kkt-box.net${NC}"

# Step 7: Summary
echo ""
echo "=================================================="
echo -e "${GREEN}Test Environment Prepared!${NC}"
echo "=================================================="
echo ""
echo "Manual steps remaining:"
echo "1. Edit $TEST_DIR/.env - update bot token and ports"
echo "2. Add Nginx location block for /test/ path"
echo "3. Reload Nginx: sudo systemctl reload nginx"
echo "4. Start test services:"
echo "   sudo systemctl start kkt-test-web"
echo "   sudo systemctl start kkt-test-bot"
echo ""
echo "Verification:"
echo "  curl http://localhost:$TEST_PORT/health"
echo "  sudo systemctl status kkt-test-web"
echo "  sudo systemctl status kkt-web  # Check production still works"
echo ""
echo "=================================================="
