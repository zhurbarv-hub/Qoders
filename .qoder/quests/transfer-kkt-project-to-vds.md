# KKT Project Migration to VDS - Design Document

## Project Context

### Current State
The KKT Services Expiration Management System is currently running in a local development environment on Windows. The system consists of:
- Backend API built with FastAPI (fully implemented and tested)
- SQLite database with complete schema
- Telegram bot module (placeholder, not implemented)
- Background scheduler module (placeholder, not implemented)
- Authentication system with JWT tokens

### Migration Objectives
Transfer the working Backend API component to a Sprintbox VDS server running Ubuntu/Debian Linux, ensuring production-ready deployment with automatic startup, proper security, and Nginx reverse proxy configuration.

---

## Target Infrastructure

### VDS Provider
**Sprintbox** - Russian VDS hosting provider

### Operating System
Ubuntu/Debian Linux (latest LTS version recommended)

### Deployment Scope
Full stack deployment including:
- Backend FastAPI application
- SQLite database with data migration
- Telegram bot integration (future implementation)
- Background scheduler (future implementation)

### Service Management
systemd service for automatic application startup and management

### Web Server
Nginx as reverse proxy for production deployment

### SSH Access
Not yet configured - requires initial setup and key generation

---

## Migration Strategy

### Phase 1: VDS Preparation and Access Setup

#### Objective
Establish secure SSH access to the VDS server and prepare the base system environment.

#### Prerequisites
- Active VDS account at Sprintbox
- VDS IP address from control panel
- Root or admin credentials received from provider
- SSH client installed on local Windows machine

#### Step-by-Step SSH Setup Guide

**Step 1.1: Install SSH Client on Windows**

Windows 10/11 includes OpenSSH by default. Verify installation:
- Open PowerShell or Command Prompt
- Run command: ssh -V
- Expected output: OpenSSH version information

If not installed:
- Open Settings → Apps → Optional Features
- Click "Add a feature"
- Find and install "OpenSSH Client"
- Restart terminal after installation

**Step 1.2: First Connection to VDS**

Connect using password provided by Sprintbox:
- Open PowerShell or Command Prompt
- Execute: ssh root@YOUR_VDS_IP
- Replace YOUR_VDS_IP with actual IP from Sprintbox panel
- On first connection, see fingerprint warning
- Type "yes" to accept and continue
- Enter password when prompted
- Successfully connected when you see server prompt

Example:
```
C:\Users\YourName> ssh root@123.45.67.89
The authenticity of host '123.45.67.89' can't be established.
Are you sure you want to continue connecting (yes/no)? yes
root@123.45.67.89's password: [enter password]
Welcome to Ubuntu...
root@vds:~#
```

**Step 1.3: Generate SSH Key Pair on Local Windows Machine**

Create SSH keys for secure passwordless authentication:
- Open PowerShell on local machine (not connected to VDS)
- Navigate to user directory: cd ~
- Generate key pair: ssh-keygen -t ed25519 -C "kkt-vds-access"
- When prompted for file location, press Enter (use default)
- When prompted for passphrase, you can:
  - Press Enter twice for no passphrase (easier but less secure)
  - Or enter strong passphrase for extra security
- Two files created in C:\Users\YourName\.ssh\:
  - id_ed25519 (private key - NEVER share this)
  - id_ed25519.pub (public key - safe to share)

**Step 1.4: Copy Public Key to VDS**

Method A - Using ssh-copy-id (if available on Windows):
- Run: ssh-copy-id -i ~/.ssh/id_ed25519.pub root@YOUR_VDS_IP
- Enter password when prompted
- Public key automatically added to VDS

Method B - Manual copy (recommended for Windows):
- Display public key content: type %USERPROFILE%\.ssh\id_ed25519.pub
- Copy the entire output (starts with "ssh-ed25519")
- Connect to VDS: ssh root@YOUR_VDS_IP
- Once connected, create .ssh directory: mkdir -p ~/.ssh
- Set directory permissions: chmod 700 ~/.ssh
- Open authorized_keys file: nano ~/.ssh/authorized_keys
- Paste your public key on new line
- Save file: Ctrl+O, Enter, Ctrl+X
- Set file permissions: chmod 600 ~/.ssh/authorized_keys
- Exit VDS: exit

**Step 1.5: Test Key-Based Authentication**

Verify passwordless login works:
- Disconnect from VDS if connected
- Try connecting: ssh root@YOUR_VDS_IP
- Should connect WITHOUT asking for password
- If asks for passphrase, that's the key passphrase (expected if you set one)
- If still asks for password, troubleshoot:
  - Check public key copied correctly
  - Verify file permissions on VDS (~/.ssh/authorized_keys should be 600)
  - Check SSH service configuration on VDS

**SSH Access Configuration**
- Generate SSH key pair on local machine using ssh-keygen ✓
- Add public key to VDS control panel or authorized_keys file ✓
- Test SSH connection with private key authentication ✓
- Disable password authentication for enhanced security (optional for now)

**System Update**
- Update package repositories to latest versions
- Upgrade all installed system packages
- Install essential build tools and utilities

**User Management**
- Create dedicated system user for application deployment (e.g., kktuser)
- Configure sudo privileges for administrative tasks
- Set up proper home directory structure

**Firewall Configuration**
- Install and enable UFW (Uncomplicated Firewall)
- Allow SSH port (22) for remote access
- Allow HTTP port (80) for web traffic
- Allow HTTPS port (443) for secure web traffic
- Enable firewall with configured rules

**Step 1.6: Update System Packages**

Once SSH access established, update the system:
- Connect to VDS: ssh root@YOUR_VDS_IP
- Update package list: apt update
- Upgrade packages: apt upgrade -y
- This may take 5-15 minutes depending on updates
- Reboot if kernel updated: reboot
- Wait 1-2 minutes, then reconnect

**Step 1.7: Create Dedicated Application User**

Create non-root user for running application:
- Create user: useradd -m -s /bin/bash kktuser
- Set password: passwd kktuser
- Enter and confirm password
- Add to sudo group: usermod -aG sudo kktuser
- Verify user created: id kktuser

Copy SSH key to new user:
- Switch to kktuser: su - kktuser
- Create .ssh directory: mkdir -p ~/.ssh
- Set permissions: chmod 700 ~/.ssh
- Exit back to root: exit
- Copy authorized_keys: cp ~/.ssh/authorized_keys /home/kktuser/.ssh/
- Set ownership: chown -R kktuser:kktuser /home/kktuser/.ssh
- Test connection: ssh kktuser@YOUR_VDS_IP (from local machine)

**Step 1.8: Configure Firewall**

Install and configure UFW firewall:
- Install UFW: apt install -y ufw
- Allow SSH first (important!): ufw allow 22/tcp
- Allow HTTP: ufw allow 80/tcp
- Allow HTTPS: ufw allow 443/tcp
- Enable firewall: ufw enable
- Confirm with "y" when prompted
- Check status: ufw status
- Should show rules active

#### Success Criteria
- ✓ SSH connection established without password prompt
- ✓ System packages updated to latest versions
- ✓ Dedicated application user (kktuser) created and functional
- ✓ Firewall active with proper rules configured
- ✓ Can connect as both root and kktuser via SSH

#### Common Issues and Solutions

**Issue: "Connection refused" when trying to connect**
- Solution: Verify VDS is running in Sprintbox control panel
- Check IP address is correct
- Ensure firewall on VDS allows port 22

**Issue: "Permission denied (publickey)"**
- Solution: Public key not properly installed
- Repeat Step 1.4 carefully
- Check ~/.ssh/authorized_keys exists on VDS
- Verify file permissions: ls -la ~/.ssh/

**Issue: Still asking for password after adding key**
- Solution: Check private key exists on local machine: dir %USERPROFILE%\.ssh\id_ed25519
- Ensure using correct username: ssh kktuser@IP (not ssh root@IP)
- Try with verbose mode to see error: ssh -v kktuser@YOUR_VDS_IP

**Issue: Lost connection during apt upgrade**
- Solution: Reconnect and check if upgrade completed: dpkg --configure -a
- If interrupted, run: apt upgrade -y again

---

### Phase 2: Python Environment Setup

#### Objective
Install and configure Python runtime environment with all required dependencies for the KKT application.

#### Activities

**Python Installation**
- Install Python 3.8 or higher using system package manager
- Install pip package manager
- Install python3-venv for virtual environment support
- Verify Python and pip installation versions

**Virtual Environment Creation**
- Create dedicated virtual environment in application directory
- Activate virtual environment for isolation
- Upgrade pip to latest version within virtual environment

**Dependencies Installation**
- Transfer requirements.txt file to VDS server
- Install all Python packages from requirements.txt
- Verify critical packages: FastAPI, uvicorn, SQLAlchemy, python-jose, passlib, aiogram
- Document any installation issues or missing system dependencies

**System Dependencies**
- Install SQLite3 development libraries if needed
- Install system packages for cryptographic operations
- Install any additional dependencies for Telegram bot (future)

#### Success Criteria
- Python 3.8+ installed and accessible
- Virtual environment created and functional
- All packages from requirements.txt installed successfully
- No import errors when testing core modules

---

### Phase 3: Application File Transfer

#### Objective
Transfer the complete KKT project codebase from local Windows environment to VDS Linux server.

#### Activities

**Directory Structure Creation**
- Create application root directory: /opt/kkt or /home/kktuser/kkt
- Create subdirectories: backend, database, bot, scheduler, logs
- Set proper ownership for application user
- Set appropriate permissions (755 for directories, 644 for files)

**File Transfer Methods**
Option A - Git clone from repository:
- Install git on VDS server
- Clone repository from https://github.com/zhurbarv-hub/Qoders
- Checkout appropriate branch (main or production)

Option B - SCP/SFTP direct transfer:
- Use scp or FileZilla to transfer project files
- Preserve directory structure during transfer
- Verify file integrity after transfer

**Configuration Files**
- Transfer .env.example as template
- Create production .env file with VDS-specific settings
- Configure database path for Linux filesystem
- Set JWT secret key (generate new for production)
- Configure API host and port settings
- Set CORS origins for production domain

**Database Migration**
- Transfer existing SQLite database file if data migration needed
- Alternatively, initialize fresh database using init_database.py script
- Run seed_data.sql for default data if required
- Verify database file permissions and ownership

#### File Path Adaptations
Windows paths require conversion to Linux format:

| Windows Path | Linux Path |
|-------------|------------|
| D:\QoProj\KKT\ | /opt/kkt/ or /home/kktuser/kkt/ |
| .\database\kkt.db | ./database/kkt.db |
| backend\main.py | backend/main.py |
| .env | .env |

#### Success Criteria
- All project files transferred to VDS
- Directory structure matches local environment
- Configuration files properly adapted for Linux
- Database accessible and functional
- File permissions set correctly

---

### Phase 4: Systemd Service Configuration

#### Objective
Configure the FastAPI application as a systemd service for automatic startup, restart on failure, and easy management.

#### Activities

**Service File Creation**
Create systemd unit file at: /etc/systemd/system/kkt-api.service

**Service Configuration Parameters**

Service metadata:
- Service name: kkt-api
- Description: KKT Services Expiration Management API
- Documentation reference to project README

Process management:
- User: kktuser (dedicated application user)
- Group: kktuser
- Working directory: /opt/kkt or /home/kktuser/kkt

Execution configuration:
- ExecStart command using virtual environment Python
- Command: /path/to/venv/bin/python -m uvicorn backend.main:app
- Host binding: 0.0.0.0 (all interfaces)
- Port: 8000 (internal, behind Nginx)
- Workers: 1 (single worker for SQLite compatibility)

Restart policy:
- Restart on failure automatically
- Restart delay: 5 seconds between attempts
- Maximum restart attempts: 5 within 10 seconds

Environment variables:
- Load from .env file or specify in service file
- Set PYTHONUNBUFFERED=1 for real-time logging

Security hardening:
- NoNewPrivileges=true to prevent privilege escalation
- PrivateTmp=true for isolated temporary files
- ReadOnlyPaths for system directories
- ProtectSystem=full for system protection

**Service Management Commands**
- Reload systemd daemon after service file creation
- Enable service for automatic startup on boot
- Start service immediately for testing
- Check service status and logs

**Logging Configuration**
- Logs managed by systemd journal
- View logs with journalctl -u kkt-api
- Configure log rotation if needed
- Monitor error logs for issues

#### Success Criteria
- Service file created and validated
- Service starts without errors
- Service restarts automatically on failure
- Service starts on system boot
- Application accessible on localhost:8000
- Logs visible in systemd journal

---

### Phase 5: Nginx Reverse Proxy Setup

#### Objective
Configure Nginx as a reverse proxy to handle HTTP requests, provide SSL termination (future), and improve security and performance.

#### Activities

**Nginx Installation**
- Install Nginx using system package manager
- Enable Nginx service for automatic startup
- Verify Nginx installation and default page access

**Configuration File Creation**
Create Nginx site configuration at: /etc/nginx/sites-available/kkt

**Proxy Configuration Parameters**

Upstream definition:
- Backend server: localhost:8000 (FastAPI application)
- Connection timeout settings
- Keepalive connections for performance

Virtual host configuration:
- Listen on port 80 (HTTP)
- Server name: VDS IP address or domain name
- Root directory and access log paths

Reverse proxy settings:
- Proxy pass to http://localhost:8000
- Preserve client IP address in headers (X-Forwarded-For)
- Preserve protocol information (X-Forwarded-Proto)
- Set proper Host header
- Disable request buffering for real-time responses

Security headers:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: enabled

Static file handling (future):
- Configure static file serving if frontend added
- Set cache control headers for performance

Request size limits:
- client_max_body_size: 10M (for file uploads if needed)

**Site Activation**
- Create symbolic link from sites-available to sites-enabled
- Test Nginx configuration syntax
- Reload Nginx to apply changes
- Verify HTTP access through Nginx

**Firewall Update**
- Ensure port 80 allowed in UFW
- Verify external access to VDS IP address
- Test API endpoints through Nginx proxy

#### Success Criteria
- Nginx installed and running
- Site configuration syntax validated
- API accessible via VDS IP address on port 80
- Proxy headers properly forwarded
- Nginx logs show incoming requests
- FastAPI application receives proxied requests correctly

---

### Phase 6: Testing and Validation

#### Objective
Verify complete system functionality in production environment and ensure all components work as expected.

#### Activities

**Health Check Validation**
- Access /health endpoint via public IP
- Verify database connection status in response
- Confirm timestamp and status fields correct

**Authentication Testing**
- Send login request to /api/auth/login
- Verify JWT token generation
- Test token validation on protected endpoints
- Confirm unauthorized access returns 401 status

**API Endpoints Testing**
Test each module:

Clients management:
- Create new client with valid INN
- Retrieve client list with pagination
- Update client information
- Search clients by name or INN
- Soft delete client

Deadlines management:
- Create deadline for existing client
- List deadlines with filtering by status (green/yellow/red)
- Update deadline expiration date
- Delete deadline

Dashboard functionality:
- Retrieve summary statistics
- Verify counts match database state
- Check urgent deadlines list
- Validate date sorting

Deadline types:
- List all deadline types
- Verify system types present (OFD, Registration, etc.)
- Test custom type creation (admin only)

Contacts management:
- Add Telegram contact for client
- List contacts for specific client
- Update contact notification settings
- Test duplicate Telegram ID validation

**Performance Testing**
- Measure response times for key endpoints
- Test concurrent request handling
- Monitor system resource usage (CPU, memory)
- Verify application stability under load

**Error Handling Validation**
- Test invalid input validation
- Verify proper error messages returned
- Check 404 responses for non-existent resources
- Confirm 500 errors logged properly

**Documentation Access**
- Access Swagger UI at /docs
- Verify all endpoints documented
- Test API calls directly from Swagger interface
- Access ReDoc at /redoc for alternative documentation view

**Database Persistence**
- Create test data through API
- Restart systemd service
- Verify data persists after restart
- Check database file integrity

**Log Monitoring**
- Review systemd journal for errors
- Check Nginx access and error logs
- Verify application logging working correctly
- Ensure no critical errors present

#### Success Criteria
- All API endpoints respond correctly
- Authentication and authorization working
- Database operations successful
- Service survives restart
- No errors in logs
- Documentation accessible
- Performance acceptable for expected load

---

### Phase 7: Security Hardening

#### Objective
Implement security best practices to protect the production system from common threats and vulnerabilities.

#### Activities

**Environment Variables Security**
- Move all sensitive data to .env file
- Set restrictive permissions on .env file (600 - owner read/write only)
- Never commit .env to version control
- Generate strong random JWT secret key
- Rotate secrets periodically

**File Permissions Audit**
- Set application directory ownership to kktuser
- Database file permissions: 640 (owner read/write, group read)
- Configuration files: 600 (owner only)
- Log files: 640 (owner read/write, group read)
- Executable scripts: 750 (owner read/write/execute, group read/execute)

**Nginx Security Enhancements**
- Hide Nginx version in headers
- Disable directory listing
- Configure rate limiting for API endpoints
- Set request timeout values
- Implement request size limits

**SSH Hardening**
- Disable root login via SSH
- Disable password authentication (key-only)
- Change default SSH port if desired
- Configure fail2ban for brute force protection
- Set up SSH connection timeout

**Firewall Rules Review**
- Verify only necessary ports open (22, 80, 443)
- Block all other incoming connections by default
- Consider IP whitelisting for SSH access
- Enable connection rate limiting

**Application Security**
- Ensure JWT tokens have reasonable expiration time
- Validate all user input on backend
- Use parameterized queries to prevent SQL injection
- Implement CORS restrictions properly
- Set secure password hashing parameters

**Database Security**
- Regular database backups scheduled
- Backup files stored securely with restricted access
- Test backup restoration procedure
- Consider encrypting sensitive data at rest

**Monitoring and Alerts**
- Set up log monitoring for suspicious activity
- Configure email alerts for service failures
- Monitor disk space usage
- Track API error rates

#### Success Criteria
- All sensitive files have restrictive permissions
- SSH access secured with keys only
- Firewall properly configured
- No security warnings in logs
- Backup system functional
- Security headers present in HTTP responses

---

## Configuration Reference

### Environment Variables (.env file)

```
Database Configuration
DATABASE_PATH=./database/kkt.db

API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false

Security Configuration
JWT_SECRET_KEY=<generate_using_secrets.token_urlsafe_32>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

CORS Configuration
CORS_ORIGINS=http://your-domain.com,https://your-domain.com

Logging Configuration
LOG_LEVEL=INFO

Telegram Bot Configuration (for future implementation)
TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_ADMIN_ID=<your_telegram_id>
```

### Systemd Service File Template

```
Service unit configuration defining how the KKT API application runs as a system service

Unit Section:
- Description: KKT Services Expiration Management API
- After: network.target (ensures network available before starting)
- Wants: network-online.target (waits for network to be fully online)

Service Section:
- Type: notify (application signals when ready)
- User: kktuser (runs as dedicated application user)
- Group: kktuser
- WorkingDirectory: /opt/kkt (application root directory)
- Environment: PYTHONUNBUFFERED=1 (immediate log output)
- ExecStart: Full path to uvicorn command with parameters
  - Uses virtual environment Python interpreter
  - Binds to 0.0.0.0:8000 (all interfaces, internal port)
  - Single worker process (SQLite requirement)
- Restart: on-failure (automatic restart if crashes)
- RestartSec: 5s (wait before restart attempt)
- StandardOutput: journal (logs to systemd journal)
- StandardError: journal

Security Hardening:
- NoNewPrivileges: true (prevent privilege escalation)
- PrivateTmp: true (isolated temporary directory)
- ProtectSystem: full (read-only system directories)

Install Section:
- WantedBy: multi-user.target (starts on system boot)
```

### Nginx Configuration Template

```
Upstream block defining backend server connection pool
- Server: localhost:8000 (FastAPI application)
- Keepalive: 32 connections (reuse connections for performance)

Server block for HTTP traffic
- Listen: 80 (HTTP port)
- Server name: VDS IP address or domain

Location block for API proxy
- Proxy pass: Forward all requests to http://localhost:8000
- Proxy headers:
  - Host: $host (preserve original host)
  - X-Real-IP: $remote_addr (client IP address)
  - X-Forwarded-For: $proxy_add_x_forwarded_for (proxy chain)
  - X-Forwarded-Proto: $scheme (HTTP or HTTPS)
- Connection settings:
  - proxy_http_version: 1.1 (use HTTP/1.1)
  - Connection: "" (enable keepalive)
- Timeouts:
  - proxy_connect_timeout: 60s
  - proxy_send_timeout: 60s
  - proxy_read_timeout: 60s

Security headers:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY

Logging:
- Access log: /var/log/nginx/kkt_access.log
- Error log: /var/log/nginx/kkt_error.log

Client settings:
- client_max_body_size: 10M (maximum request size)
```

---

## Deployment Checklist

### Pre-Deployment Preparation
- [ ] VDS server provisioned from Sprintbox
- [ ] Ubuntu/Debian Linux installed and accessible
- [ ] Root or sudo access available
- [ ] Server IP address documented
- [ ] Local project files ready for transfer
- [ ] requirements.txt file up to date

### Phase 1: VDS Access Setup
- [ ] SSH key pair generated on local machine
- [ ] Public key added to VDS authorized_keys
- [ ] SSH connection tested successfully
- [ ] System packages updated (apt update && apt upgrade)
- [ ] Application user created (kktuser)
- [ ] UFW firewall installed and configured
- [ ] Firewall rules: SSH (22), HTTP (80), HTTPS (443) allowed
- [ ] Firewall enabled and active

### Phase 2: Python Environment
- [ ] Python 3.8+ installed
- [ ] pip package manager installed
- [ ] python3-venv package installed
- [ ] Virtual environment created in application directory
- [ ] Virtual environment activated
- [ ] pip upgraded to latest version in venv
- [ ] requirements.txt transferred to server
- [ ] All dependencies installed from requirements.txt
- [ ] SQLite3 system libraries verified
- [ ] Import test successful for FastAPI and core modules

### Phase 3: Application Transfer
- [ ] Application directory created (/opt/kkt or ~/kkt)
- [ ] Subdirectories created (backend, database, bot, scheduler, logs)
- [ ] Project files transferred via git clone or SCP
- [ ] Directory structure verified
- [ ] .env file created with production settings
- [ ] Database file transferred or initialized
- [ ] File ownership set to kktuser
- [ ] File permissions configured (directories 755, files 644)
- [ ] Configuration paths updated for Linux
- [ ] Test application startup manually with uvicorn

### Phase 4: Systemd Service
- [ ] Service file created: /etc/systemd/system/kkt-api.service
- [ ] Service file contains correct paths and user
- [ ] Environment variables configured in service
- [ ] Security hardening parameters added
- [ ] systemd daemon reloaded
- [ ] Service enabled for automatic startup
- [ ] Service started successfully
- [ ] Service status shows active (running)
- [ ] Application accessible on localhost:8000
- [ ] Logs visible in journalctl -u kkt-api
- [ ] Service restarts automatically after manual stop

### Phase 5: Nginx Setup
- [ ] Nginx installed via apt
- [ ] Nginx service enabled and running
- [ ] Site configuration created: /etc/nginx/sites-available/kkt
- [ ] Upstream backend configured (localhost:8000)
- [ ] Proxy headers configured correctly
- [ ] Security headers added
- [ ] Site enabled (symlink to sites-enabled)
- [ ] Nginx configuration syntax tested (nginx -t)
- [ ] Nginx service reloaded
- [ ] API accessible via VDS IP address on port 80
- [ ] Access logs show incoming requests
- [ ] Error logs contain no critical issues

### Phase 6: Testing
- [ ] Health check endpoint accessible via public IP
- [ ] Database connection confirmed in health check
- [ ] Login endpoint returns JWT token
- [ ] Protected endpoints require authentication
- [ ] Clients CRUD operations working
- [ ] Deadlines CRUD operations working
- [ ] Dashboard statistics accurate
- [ ] Deadline types listing correct
- [ ] Contacts management functional
- [ ] Swagger UI accessible at /docs
- [ ] ReDoc accessible at /redoc
- [ ] API documentation complete and accurate
- [ ] Service restart preserves data
- [ ] Response times acceptable
- [ ] No errors in systemd logs
- [ ] No errors in Nginx logs

### Phase 7: Security
- [ ] .env file permissions set to 600
- [ ] JWT secret key generated and unique
- [ ] Database file permissions set to 640
- [ ] Application files owned by kktuser
- [ ] Root login disabled in SSH
- [ ] Password authentication disabled in SSH
- [ ] Only key-based SSH access allowed
- [ ] fail2ban installed and configured
- [ ] Firewall rules reviewed and minimal
- [ ] Nginx version hidden in headers
- [ ] Rate limiting configured in Nginx
- [ ] CORS origins properly restricted
- [ ] Database backup script created
- [ ] Backup tested and restorable
- [ ] Log monitoring configured

### Post-Deployment
- [ ] DNS configured to point to VDS IP (if using domain)
- [ ] SSL certificate obtained and configured (Let's Encrypt recommended)
- [ ] Nginx HTTPS configuration added
- [ ] HTTP to HTTPS redirect configured
- [ ] Application monitoring set up
- [ ] Alert system configured for failures
- [ ] Documentation updated with production details
- [ ] Team access credentials distributed securely
- [ ] Rollback plan documented
- [ ] Maintenance schedule planned

---

## Command Reference

### SSH and Server Access

Generate SSH key pair on local machine:
```
ssh-keygen -t ed25519 -C "kkt-vds-access"
```

Copy public key to VDS:
```
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@vds-ip-address
```

Connect to VDS via SSH:
```
ssh -i ~/.ssh/id_ed25519 user@vds-ip-address
```

### System Setup Commands

Update package repositories:
```
sudo apt update
```

Upgrade installed packages:
```
sudo apt upgrade -y
```

Install essential build tools:
```
sudo apt install -y build-essential git curl wget
```

Create application user:
```
sudo useradd -m -s /bin/bash kktuser
sudo usermod -aG sudo kktuser
```

Configure firewall:
```
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

### Python Environment Commands

Install Python and related packages:
```
sudo apt install -y python3 python3-pip python3-venv python3-dev
```

Create virtual environment:
```
cd /opt/kkt
python3 -m venv venv
```

Activate virtual environment:
```
source venv/bin/activate
```

Install Python dependencies:
```
pip install --upgrade pip
pip install -r requirements.txt
```

### Application Transfer Commands

Clone from Git repository:
```
git clone https://github.com/zhurbarv-hub/Qoders.git /opt/kkt
```

Transfer files via SCP (from local Windows machine):
```
scp -r D:\QoProj\KKT\* user@vds-ip:/opt/kkt/
```

Set file ownership:
```
sudo chown -R kktuser:kktuser /opt/kkt
```

Set directory permissions:
```
sudo find /opt/kkt -type d -exec chmod 755 {} \;
sudo find /opt/kkt -type f -exec chmod 644 {} \;
```

Set executable permissions for scripts:
```
chmod +x /opt/kkt/database/init_database.py
```

### Database Setup Commands

Initialize database:
```
cd /opt/kkt
source venv/bin/activate
python database/init_database.py
```

Set database permissions:
```
chmod 640 /opt/kkt/database/kkt.db
```

### Systemd Service Commands

Create systemd service file:
```
sudo nano /etc/systemd/system/kkt-api.service
```

Reload systemd daemon:
```
sudo systemctl daemon-reload
```

Enable service for autostart:
```
sudo systemctl enable kkt-api
```

Start service:
```
sudo systemctl start kkt-api
```

Check service status:
```
sudo systemctl status kkt-api
```

Stop service:
```
sudo systemctl stop kkt-api
```

Restart service:
```
sudo systemctl restart kkt-api
```

View service logs:
```
sudo journalctl -u kkt-api -f
```

View last 100 log entries:
```
sudo journalctl -u kkt-api -n 100
```

### Nginx Commands

Install Nginx:
```
sudo apt install -y nginx
```

Create site configuration:
```
sudo nano /etc/nginx/sites-available/kkt
```

Enable site:
```
sudo ln -s /etc/nginx/sites-available/kkt /etc/nginx/sites-enabled/
```

Test Nginx configuration:
```
sudo nginx -t
```

Reload Nginx:
```
sudo systemctl reload nginx
```

Restart Nginx:
```
sudo systemctl restart nginx
```

View Nginx access logs:
```
sudo tail -f /var/log/nginx/kkt_access.log
```

View Nginx error logs:
```
sudo tail -f /var/log/nginx/kkt_error.log
```

### Testing and Validation Commands

Test health endpoint:
```
curl http://vds-ip-address/health
```

Test login endpoint:
```
curl -X POST http://vds-ip-address/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kkt.local","password":"admin123"}'
```

Test authenticated endpoint (replace TOKEN):
```
curl http://vds-ip-address/api/clients \
  -H "Authorization: Bearer TOKEN"
```

Check listening ports:
```
sudo netstat -tulpn | grep LISTEN
```

Monitor system resources:
```
htop
```

Check disk space:
```
df -h
```

### Security Commands

Generate JWT secret key:
```
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set .env file permissions:
```
chmod 600 /opt/kkt/.env
```

Install fail2ban:
```
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

View failed login attempts:
```
sudo fail2ban-client status sshd
```

### Backup Commands

Create database backup:
```
cp /opt/kkt/database/kkt.db /opt/kkt/database/backups/kkt_$(date +%Y%m%d_%H%M%S).db
```

Create full application backup:
```
tar -czf /backup/kkt_backup_$(date +%Y%m%d).tar.gz -C /opt kkt
```

### Troubleshooting Commands

Check if application is running:
```
ps aux | grep uvicorn
```

Check port 8000 is listening:
```
sudo lsof -i :8000
```

Test application directly (bypass Nginx):
```
curl http://localhost:8000/health
```

View all systemd service logs:
```
sudo journalctl -xe
```

Check Nginx configuration for errors:
```
sudo nginx -t
```

Restart all services:
```
sudo systemctl restart kkt-api nginx
```

---

## Troubleshooting Guide

### Issue: SSH Connection Refused

**Symptoms:**
- Cannot connect to VDS via SSH
- Connection timeout or "Connection refused" error

**Possible Causes:**
- SSH service not running on VDS
- Firewall blocking port 22
- Wrong IP address or port
- Network connectivity issues

**Resolution Steps:**
1. Verify VDS is running in Sprintbox control panel
2. Check firewall allows port 22: sudo ufw status
3. Ensure SSH service running: sudo systemctl status ssh
4. Test connection from different network
5. Contact Sprintbox support if persistent

---

### Issue: Python Module Import Errors

**Symptoms:**
- ModuleNotFoundError when starting application
- ImportError for FastAPI, uvicorn, or other dependencies

**Possible Causes:**
- Virtual environment not activated
- Dependencies not installed
- Wrong Python version
- Corrupted virtual environment

**Resolution Steps:**
1. Activate virtual environment: source /opt/kkt/venv/bin/activate
2. Verify Python version: python --version (should be 3.8+)
3. Reinstall dependencies: pip install -r requirements.txt
4. Check for errors during installation
5. Recreate virtual environment if necessary
6. Ensure systemd service uses correct venv Python path

---

### Issue: Database Connection Failed

**Symptoms:**
- Health check shows "database: disconnected"
- SQLite errors in logs
- Cannot read or write data

**Possible Causes:**
- Database file missing or wrong path
- Incorrect file permissions
- Database file corrupted
- Path format incorrect for Linux

**Resolution Steps:**
1. Verify database file exists: ls -l /opt/kkt/database/kkt.db
2. Check file permissions: should be 640 or 664
3. Set ownership: sudo chown kktuser:kktuser /opt/kkt/database/kkt.db
4. Verify path in .env uses forward slashes (Linux format)
5. Initialize database if missing: python database/init_database.py
6. Test database manually: sqlite3 /opt/kkt/database/kkt.db ".tables"

---

### Issue: Systemd Service Fails to Start

**Symptoms:**
- Service status shows "failed" or "inactive (dead)"
- Application not accessible
- Errors in journalctl logs

**Possible Causes:**
- Incorrect paths in service file
- Wrong user or permissions
- Port already in use
- Application errors
- Missing dependencies

**Resolution Steps:**
1. Check service logs: sudo journalctl -u kkt-api -n 50
2. Verify service file syntax: systemctl cat kkt-api
3. Test manual startup: sudo -u kktuser /opt/kkt/venv/bin/python -m uvicorn backend.main:app
4. Check port availability: sudo lsof -i :8000
5. Verify working directory exists and accessible
6. Ensure .env file present and readable
7. Check Python path in ExecStart is correct
8. Reload daemon after changes: sudo systemctl daemon-reload

---

### Issue: Nginx 502 Bad Gateway

**Symptoms:**
- Accessing VDS IP returns 502 error
- Nginx error log shows "Connection refused" to upstream

**Possible Causes:**
- FastAPI application not running
- Wrong upstream port in Nginx config
- Firewall blocking internal connections
- Application crashed

**Resolution Steps:**
1. Verify kkt-api service running: sudo systemctl status kkt-api
2. Test backend directly: curl http://localhost:8000/health
3. Check Nginx upstream configuration points to localhost:8000
4. Review Nginx error log: sudo tail -f /var/log/nginx/kkt_error.log
5. Restart both services: sudo systemctl restart kkt-api nginx
6. Check for port conflicts: sudo netstat -tulpn | grep 8000
7. Verify no firewall rules blocking localhost connections

---

### Issue: 401 Unauthorized on Protected Endpoints

**Symptoms:**
- Cannot access API endpoints requiring authentication
- Login works but subsequent requests fail
- Token appears valid but rejected

**Possible Causes:**
- JWT secret key mismatch
- Token expired
- Token not included in request header
- CORS blocking credentials
- Wrong Authorization header format

**Resolution Steps:**
1. Verify JWT_SECRET_KEY same in .env file
2. Check token expiration time in settings
3. Ensure Authorization header format: "Bearer <token>"
4. Test token immediately after login
5. Review CORS settings in .env
6. Check application logs for authentication errors
7. Generate new token and retry
8. Verify user exists in database: sqlite3 database/kkt.db "SELECT * FROM users;"

---

### Issue: High Memory or CPU Usage

**Symptoms:**
- VDS becomes slow or unresponsive
- Application performance degrades
- Out of memory errors

**Possible Causes:**
- Too many uvicorn workers
- Memory leak in application
- Insufficient VDS resources
- Database not optimized
- Many concurrent connections

**Resolution Steps:**
1. Monitor resource usage: htop or top
2. Check uvicorn worker count in service file (should be 1 for SQLite)
3. Review application logs for errors
4. Restart service to clear memory: sudo systemctl restart kkt-api
5. Optimize database queries
6. Consider upgrading VDS plan if resources insufficient
7. Implement connection pooling and limits
8. Add monitoring and alerts for resource usage

---

### Issue: Cannot Access API from External Network

**Symptoms:**
- API works on VDS localhost but not from internet
- Timeout when accessing public IP
- Works locally but not remotely

**Possible Causes:**
- Firewall blocking HTTP port 80
- Nginx not listening on public interface
- VDS provider network restrictions
- Wrong IP address
- DNS not configured

**Resolution Steps:**
1. Check firewall allows port 80: sudo ufw status
2. Verify Nginx listening on 0.0.0.0:80: sudo netstat -tulpn | grep :80
3. Test from VDS itself: curl http://localhost/health
4. Verify public IP address is correct: curl ifconfig.me
5. Check Sprintbox firewall/security group settings
6. Test with curl from external machine: curl http://vds-ip/health
7. Review Nginx configuration server_name directive
8. Check VDS provider network configuration

---

### Issue: Database Locked Errors

**Symptoms:**
- "Database is locked" errors in logs
- Writes fail intermittently
- Concurrent request failures

**Possible Causes:**
- Multiple uvicorn workers with SQLite
- Long-running transactions
- Backup process accessing database
- Multiple application instances

**Resolution Steps:**
1. Ensure only 1 uvicorn worker in systemd service
2. Implement proper database connection handling
3. Reduce transaction duration
4. Add retry logic for locked database
5. Consider connection pooling with timeout
6. Ensure backup scripts not locking database
7. Check for zombie processes: ps aux | grep uvicorn
8. Migrate to PostgreSQL if concurrency required

---

## Future Enhancements

### Telegram Bot Implementation
After successful backend deployment, implement Telegram bot functionality:
- Install aiogram library dependencies
- Configure bot token in .env file
- Implement notification sending logic
- Connect bot to backend API for deadline alerts
- Create systemd service for bot process
- Test notification delivery to contacts

### Background Scheduler Service
Implement automated deadline checking:
- Create scheduler script using APScheduler library
- Configure daily checks for expiring deadlines
- Integrate with Telegram bot for notifications
- Set up as separate systemd service
- Configure error handling and logging
- Test automated notification flow

### SSL Certificate Configuration
Secure the application with HTTPS:
- Install certbot for Let's Encrypt
- Obtain SSL certificate for domain
- Configure Nginx HTTPS virtual host
- Set up automatic certificate renewal
- Redirect HTTP to HTTPS
- Update CORS settings for HTTPS origin

### Web Frontend Deployment
If frontend interface developed:
- Build frontend static files
- Configure Nginx to serve static content
- Set up frontend routing
- Integrate with backend API
- Configure production build optimizations
- Implement caching strategies

### Database Backup Automation
Implement automated backup system:
- Create backup script with rotation policy
- Schedule daily backups via cron
- Store backups in separate location
- Implement backup verification
- Configure backup retention period
- Test restoration procedure regularly

### Monitoring and Alerting
Implement comprehensive monitoring:
- Install monitoring tools (Prometheus, Grafana)
- Set up application metrics collection
- Configure email alerts for critical issues
- Monitor API response times
- Track error rates and types
- Set up uptime monitoring
- Create dashboard for key metrics

### Load Balancing and Scaling
Prepare for increased traffic:
- Migrate from SQLite to PostgreSQL
- Configure multiple uvicorn workers
- Implement load balancer if multiple servers
- Set up database replication
- Configure session management for distributed system
- Implement caching layer (Redis)

### CI/CD Pipeline
Automate deployment process:
- Set up Git hooks for automated deployment
- Create deployment scripts
- Implement automated testing before deployment
- Configure rollback mechanism
- Set up staging environment
- Implement blue-green deployment strategy

---

## Risk Assessment

### High Priority Risks

**Risk: Data Loss During Migration**
- Impact: Critical business data lost or corrupted
- Probability: Medium
- Mitigation: Create complete backup before migration, test database integrity after transfer, verify data completeness
- Contingency: Maintain local database copy until migration validated, document rollback procedure

**Risk: Service Downtime**
- Impact: API unavailable during migration period
- Probability: High
- Mitigation: Plan migration during low-traffic period, prepare all files before cutting over, test thoroughly in staging
- Contingency: Keep local development environment running as backup, communicate downtime window to stakeholders

**Risk: Security Breach**
- Impact: Unauthorized access to system or data
- Probability: Medium
- Mitigation: Implement all security hardening steps, use strong passwords and keys, configure firewall properly
- Contingency: Monitor logs for suspicious activity, prepare incident response plan, maintain secure backups

### Medium Priority Risks

**Risk: Configuration Errors**
- Impact: Application fails to start or functions incorrectly
- Probability: Medium
- Mitigation: Follow checklist systematically, test each component independently, validate configurations before proceeding
- Contingency: Document all configuration changes, maintain working configuration backups, test rollback procedure

**Risk: Performance Issues**
- Impact: Slow response times or system overload
- Probability: Low to Medium
- Mitigation: Monitor resource usage, optimize queries, configure appropriate limits, choose adequate VDS plan
- Contingency: Implement caching, optimize database, upgrade VDS resources if needed

**Risk: Dependency Conflicts**
- Impact: Application fails due to missing or incompatible packages
- Probability: Low
- Mitigation: Use virtual environment, freeze exact versions in requirements.txt, test all imports
- Contingency: Document working package versions, maintain fallback environment

### Low Priority Risks

**Risk: Network Connectivity Issues**
- Impact: Cannot access VDS or API intermittently
- Probability: Low
- Mitigation: Choose reliable VDS provider, configure proper timeouts, implement retry logic
- Contingency: Monitor uptime, configure failover if critical, contact provider support

**Risk: Insufficient Resources**
- Impact: System crashes due to resource exhaustion
- Probability: Low
- Mitigation: Monitor resource usage, choose appropriate VDS plan, implement resource limits
- Contingency: Upgrade VDS plan, optimize application, implement autoscaling if available

---

## Success Metrics

### Technical Metrics

**Availability:**
- Target: 99.5% uptime
- Measurement: Monitor health check endpoint availability
- Threshold: Less than 3.6 hours downtime per month

**Performance:**
- Target: API response time < 200ms for 95% of requests
- Measurement: Nginx access logs analysis, application monitoring
- Threshold: Alert if P95 latency exceeds 500ms

**Reliability:**
- Target: Zero data loss during migration
- Measurement: Data integrity checks, record counts comparison
- Threshold: 100% data accuracy required

**Security:**
- Target: Zero security incidents
- Measurement: Log analysis, intrusion detection, security audit
- Threshold: Immediate action on any security alert

### Operational Metrics

**Deployment Speed:**
- Target: Complete migration within 4-6 hours
- Measurement: Time tracking from start to production validation
- Threshold: Rollback if exceeds 8 hours

**Recovery Time:**
- Target: Service restart < 30 seconds
- Measurement: systemd service restart duration
- Threshold: Investigate if restart exceeds 60 seconds

**Backup Success:**
- Target: 100% successful daily backups
- Measurement: Backup script execution logs
- Threshold: Alert on any backup failure

### Business Metrics

**User Satisfaction:**
- Target: No increase in user complaints about performance
- Measurement: Support ticket tracking, user feedback
- Threshold: Investigate if complaints increase by 10%

**Cost Efficiency:**
- Target: VDS costs within budget
- Measurement: Monthly billing from Sprintbox
- Threshold: Alert if costs exceed projected budget by 20%

**Scalability Readiness:**
- Target: Ability to handle 2x current load
- Measurement: Load testing results
- Threshold: Must handle peak load with < 5% error rate

---

# APPENDIX: Phase 3 - Telegram Bot Implementation Design

## Overview

This appendix contains the design for implementing Telegram Bot functionality (Phase 3 of the KKT project). This feature will be developed locally before being deployed to VDS using the migration strategy outlined in the main document.

## Project Context

### Current System State
- Phase 1: Foundation setup - COMPLETED
- Phase 2: Backend API (FastAPI) - COMPLETED
- Phase 3: Telegram Bot - TO BE IMPLEMENTED
- Phase 4: Background Scheduler - PLANNED
- Phase 5: Web Interface - PLANNED

### Integration Points
- Existing FastAPI backend with authentication
- SQLite database with clients, deadlines, and contacts tables
- Notification logs table for tracking sent messages

---

## Functional Requirements

### Core Features

**Automated Notifications**
- Send deadline expiration alerts automatically
- Notify at 14, 7, and 3 days before expiration
- Send to both administrator and client contacts
- Track notification history to prevent duplicates

**Bot Commands**
- /start - Initialize bot and display welcome message
- /help - Show available commands
- /status - Display current deadline statistics
- /list - Show upcoming deadlines
- /check - Manually trigger deadline check
- /today - Show deadlines expiring today
- /week - Show deadlines expiring this week

**User Management**
- Administrator authentication using Telegram ID
- Client contact verification against database
- Role-based command access (admin vs client)

### Notification Logic

**Trigger Conditions**
Deadline notification sent when:
- Days until expiration equals 14, 7, or 3
- Notification for this deadline and period not yet sent
- Contact has notifications enabled
- Contact has valid Telegram ID

**Message Content**
Notification includes:
- Client name and INN
- Deadline type (OFD, Registration, etc.)
- Expiration date
- Days remaining
- Urgency indicator (🟢 green, 🟡 yellow, 🔴 red)

**Delivery Strategy**
- Send to administrator for all deadlines
- Send to client contacts only for their organization
- Retry failed deliveries with exponential backoff
- Log all delivery attempts and results

---

## Technical Architecture

### Technology Stack

**Bot Framework**
- Library: aiogram 3.x (async Telegram Bot API wrapper)
- Python version: 3.8+ (compatible with existing backend)
- Async/await pattern for concurrent operations

**Integration Components**
- Database: Direct SQLite access using existing models
- API: Optional HTTP calls to FastAPI endpoints
- Scheduler: APScheduler for periodic checks

### Module Structure

**bot/ directory organization:**
```
bot/
├── __init__.py
├── main.py              # Bot entry point and initialization
├── config.py            # Bot-specific configuration
├── handlers/            # Command and message handlers
│   ├── __init__.py
│   ├── admin.py         # Admin-only commands
│   ├── common.py        # Public commands (/start, /help)
│   └── deadlines.py     # Deadline-related commands
├── services/            # Business logic
│   ├── __init__.py
│   ├── notifier.py      # Notification sending logic
│   ├── checker.py       # Deadline checking logic
│   └── formatter.py     # Message formatting
├── middlewares/         # Request processing
│   ├── __init__.py
│   ├── auth.py          # User authentication
│   └── logging.py       # Request logging
└── utils/
    ├── __init__.py
    └── helpers.py       # Utility functions
```

### Component Responsibilities

**Bot Main (main.py)**
- Initialize bot instance with token
- Register handlers and middlewares
- Configure dispatcher
- Start polling or webhook
- Handle graceful shutdown

**Handlers**
- Receive and parse user commands
- Validate user permissions
- Call appropriate services
- Format and send responses

**Services**
- Notifier: Compose and send notifications
- Checker: Query database for expiring deadlines
- Formatter: Create message text with formatting

**Middlewares**
- Auth: Verify user identity and permissions
- Logging: Record command usage and errors

---

## Data Flow

### Automated Notification Flow

1. Scheduler triggers deadline check (daily at configured time)
2. Checker service queries database for deadlines expiring in 14/7/3 days
3. For each deadline, filter contacts where notifications enabled
4. Check notification_logs to avoid duplicate sends
5. Notifier service composes message with deadline details
6. Send message to each recipient via Telegram API
7. Record delivery result in notification_logs table
8. Retry failed deliveries with delay

### Command Execution Flow

1. User sends command to bot
2. Middleware authenticates user by Telegram ID
3. Middleware checks user role (admin/client)
4. Handler receives command and extracts parameters
5. Handler calls service to fetch data from database
6. Service queries database and returns results
7. Handler formats response using formatter service
8. Bot sends formatted message to user

### Manual Check Flow (/check command)

1. Admin sends /check command
2. Auth middleware verifies admin role
3. Handler triggers immediate deadline check
4. Checker service executes same logic as automated check
5. Notifier sends notifications to all recipients
6. Handler confirms completion to admin with statistics

---

## Database Integration

### Tables Used

**contacts table**
- Read telegram_id for message delivery
- Check notifications_enabled flag
- Filter by client_id for targeted notifications

**deadlines table with joins**
- Query via v_expiring_soon view
- Join with clients for organization details
- Join with deadline_types for service type

**notification_logs table**
- Insert record for each notification attempt
- Query to prevent duplicate notifications
- Track delivery status and errors

### Query Patterns

**Find deadlines requiring notification:**
```
Query v_expiring_soon view filtered by:
- days_until_expiration IN (14, 7, 3)
- status = 'active'
- NOT EXISTS matching notification in logs
```

**Get recipients for deadline:**
```
Join contacts table on client_id where:
- notifications_enabled = true
- telegram_id IS NOT NULL
- telegram_id != '' (not empty string)
```

**Record notification attempt:**
```
Insert into notification_logs:
- deadline_id
- contact_id or admin flag
- notification_type (14_days, 7_days, 3_days)
- sent_at timestamp
- delivery_status
- error_message if failed
```

---

## Configuration

### Environment Variables

Add to .env file:

```
Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_ADMIN_ID=your_telegram_user_id

Notification Schedule
NOTIFICATION_CHECK_TIME=09:00
NOTIFICATION_TIMEZONE=Europe/Moscow

Notification Settings
NOTIFICATION_RETRY_ATTEMPTS=3
NOTIFICATION_RETRY_DELAY=300
NOTIFICATION_DAYS=[14,7,3]
```

### Bot Configuration Class

Extend backend/config.py Settings class:

```
New fields for Telegram bot:
- telegram_bot_token: str (required)
- telegram_admin_id: int (required)
- notification_check_time: str (default "09:00")
- notification_timezone: str (default "UTC")
- notification_retry_attempts: int (default 3)
- notification_retry_delay: int (default 300)
- notification_days: list[int] (default [14, 7, 3])
```

---

## Message Templates

### Welcome Message (/start)

```
Welcome message structure:
- Greeting with bot name
- Brief description of functionality
- List of available commands
- Instructions for admin vs client users
```

### Deadline Notification

```
Notification format:

Emoji indicator (🟢/🟡/🔴) + Urgency level

Client Information:
- Organization name
- INN number

Deadline Details:
- Service type
- Expiration date (formatted)
- Days remaining

Action items or notes
```

### Status Response (/status)

```
Statistics display:

Total Deadlines: X
- 🟢 Green (safe): X
- 🟡 Yellow (warning): X  
- 🔴 Red (urgent): X

Expiring Soon:
- Next 7 days: X
- Next 14 days: X
- Next 30 days: X
```

### Deadline List (/list, /week, /today)

```
List format for each deadline:

[Status Emoji] Client Name (INN)
Service: Deadline Type
Expires: Date (X days)
---
```

---

## Security Considerations

### Authentication

**Admin Verification**
- Compare user Telegram ID with TELEGRAM_ADMIN_ID from config
- Reject admin commands from unauthorized users
- Log unauthorized access attempts

**Client Verification**
- Look up user Telegram ID in contacts table
- Verify contact belongs to valid client
- Filter data to show only user's organization

### Data Protection

**Sensitive Information**
- Never expose full database in error messages
- Sanitize client data in logs
- Limit information in client-facing messages

**Rate Limiting**
- Implement command throttling per user
- Prevent spam and abuse
- Configure max requests per minute

### Error Handling

**User-Facing Errors**
- Generic error messages for users
- Specific errors only for admin
- Avoid exposing system internals

**System Errors**
- Log all exceptions with full context
- Alert admin on critical failures
- Implement automatic recovery where possible

---

## Scheduler Integration

### APScheduler Configuration

**Job Definition**
- Job type: Cron trigger
- Schedule: Daily at configured time
- Timezone: From configuration
- Max instances: 1 (prevent overlapping runs)

**Execution Flow**
1. Scheduler initializes on bot startup
2. Cron job triggers at specified time
3. Async task calls checker service
4. Checker queries database and sends notifications
5. Results logged for monitoring

**Manual Trigger**
- Admin /check command bypasses schedule
- Executes same check logic immediately
- Provides feedback on notifications sent

### Error Recovery

**Job Failure Handling**
- Log failure with full traceback
- Send error notification to admin
- Schedule retry based on error type
- Alert if consecutive failures exceed threshold

**Database Connection Issues**
- Retry with exponential backoff
- Use connection pooling
- Implement circuit breaker pattern

---

## Testing Strategy

### Unit Tests

**Services Testing**
- Mock database queries
- Test notification logic with various deadline scenarios
- Verify message formatting
- Test error handling paths

**Handlers Testing**
- Mock Telegram API calls
- Test command parsing
- Verify permission checks
- Test response formatting

### Integration Tests

**Database Integration**
- Use test database with sample data
- Verify query correctness
- Test transaction handling
- Check notification log creation

**Bot Integration**
- Use Telegram Bot API test environment
- Send test commands
- Verify responses
- Test notification delivery

### Manual Testing

**Command Testing**
- Execute each command as admin
- Execute allowed commands as client
- Verify unauthorized access rejection
- Test edge cases and invalid inputs

**Notification Testing**
- Create test deadlines expiring in 14/7/3 days
- Trigger manual check
- Verify notifications sent to correct recipients
- Check notification log entries

---

## Deployment Considerations

### Local Development

**Running the Bot**
- Execute as separate Python process
- Use polling mode for local testing
- Hot reload on code changes during development

**Testing with Real Telegram**
- Create test bot with @BotFather
- Use test Telegram account for client role
- Verify all commands and notifications

### Production Deployment

**Process Management**
- Run as separate systemd service (bot.service)
- Independent from FastAPI service
- Auto-restart on failure
- Proper logging configuration

**Webhook vs Polling**
- Polling: Simpler, suitable for moderate load
- Webhook: More efficient, requires HTTPS
- Choose based on VDS capabilities

**Resource Requirements**
- Memory: ~100-200 MB
- CPU: Minimal (async I/O bound)
- Network: Outbound HTTPS to Telegram API

---

## Monitoring and Logging

### Metrics to Track

**Bot Health**
- Uptime and connection status
- API request success/failure rate
- Command execution count
- Average response time

**Notification Metrics**
- Notifications sent per day
- Delivery success rate
- Failed delivery reasons
- Duplicate prevention effectiveness

**User Activity**
- Command usage frequency
- Active users count
- Error rate per user

### Log Levels

**DEBUG**
- Command parsing details
- Database query execution
- Message formatting steps

**INFO**
- Bot startup/shutdown
- Scheduled job execution
- Successful command execution
- Notifications sent

**WARNING**
- Retry attempts
- Rate limit warnings
- Minor configuration issues

**ERROR**
- Failed notifications
- Database connection errors
- Telegram API errors
- Unhandled exceptions

### Log Storage

**File Logging**
- Rotating file handler
- Max size: 10 MB per file
- Keep last 5 files
- Location: logs/bot.log

**Structured Logging**
- JSON format for easy parsing
- Include timestamp, level, module, message
- Add context: user_id, command, deadline_id

---

## Implementation Phases

### Phase 3.1: Basic Bot Setup (Week 4, Days 1-2)

**Objectives:**
- Initialize bot project structure
- Configure bot token and admin ID
- Implement /start and /help commands
- Test basic connectivity

**Deliverables:**
- bot/main.py with initialization
- bot/config.py with settings
- Basic command handlers
- Connection verification

### Phase 3.2: Command Implementation (Week 4, Days 3-4)

**Objectives:**
- Implement all informational commands
- Add authentication middleware
- Create message formatters
- Test command execution

**Deliverables:**
- All handlers implemented
- Auth middleware functional
- Formatter service complete
- Command tests passing

### Phase 3.3: Notification System (Week 4, Days 5-7)

**Objectives:**
- Implement notification checker
- Create notification sender
- Add notification logging
- Test notification flow

**Deliverables:**
- Checker service complete
- Notifier service functional
- Database integration working
- Notification tests passing

### Phase 3.4: Scheduler Integration (Week 5, Days 1-2)

**Objectives:**
- Integrate APScheduler
- Configure daily job
- Implement manual trigger
- Test scheduled execution

**Deliverables:**
- Scheduler configured
- Cron job functional
- Manual check working
- Schedule tests passing

### Phase 3.5: Testing and Polish (Week 5, Days 3-5)

**Objectives:**
- Complete unit test coverage
- Perform integration testing
- Fix identified bugs
- Optimize performance

**Deliverables:**
- >80% test coverage
- All tests passing
- Bug fixes applied
- Documentation complete

---

## Success Criteria

### Functional Requirements
- ✓ Bot responds to all specified commands
- ✓ Notifications sent at correct intervals (14, 7, 3 days)
- ✓ Admin receives all deadline notifications
- ✓ Clients receive only their organization's notifications
- ✓ No duplicate notifications sent
- ✓ Failed notifications logged and retried

### Technical Requirements
- ✓ Bot maintains stable connection to Telegram
- ✓ Response time < 2 seconds for commands
- ✓ Scheduler executes daily without manual intervention
- ✓ Database queries optimized (< 100ms)
- ✓ Error handling prevents bot crashes

### Quality Requirements
- ✓ Unit test coverage > 80%
- ✓ Integration tests cover main flows
- ✓ Code follows project style guidelines
- ✓ Documentation complete and accurate
- ✓ No critical security vulnerabilities

---

## Future Enhancements

### Phase 3.5+: Advanced Features

**Interactive Notifications**
- Inline buttons for quick actions
- Mark as handled
- Snooze notification
- View full details

**Client Self-Service**
- Register Telegram ID via bot
- Update notification preferences
- View deadline history
- Request deadline extension

**Advanced Admin Tools**
- Add/edit deadlines via bot
- Bulk notification management
- Generate reports
- Export data

**Analytics and Insights**
- Notification effectiveness tracking
- User engagement metrics
- Deadline trend analysis
- Automated recommendations

**Multi-Language Support**
- Russian and English interfaces
- Configurable per user
- Localized date/time formats

---

## Dependencies and Prerequisites

### Required Python Packages

Add to requirements.txt:
```
aiogram>=3.0.0
APScheduler>=3.10.0
pytz>=2023.3
```

### Telegram Setup

**Create Bot**
1. Message @BotFather on Telegram
2. Send /newbot command
3. Follow prompts to name bot
4. Receive bot token
5. Save token securely

**Configure Bot**
1. Set bot description with @BotFather
2. Set command list for autocomplete
3. Configure privacy settings
4. Optional: Set bot profile picture

**Get Admin Telegram ID**
1. Message @userinfobot
2. Receive your Telegram user ID
3. Add to configuration as TELEGRAM_ADMIN_ID

### Database Schema

No schema changes required - uses existing:
- clients table
- deadlines table  
- deadline_types table
- contacts table
- notification_logs table
- v_expiring_soon view

---

## Risk Assessment

### High Priority Risks

**Risk: Telegram API Rate Limiting**
- Impact: Notifications delayed or blocked
- Probability: Medium
- Mitigation: Implement rate limiting, batch notifications, use queue
- Contingency: Alert admin, retry with delays

**Risk: Bot Token Exposure**
- Impact: Unauthorized bot access
- Probability: Low
- Mitigation: Store in .env, never commit, rotate periodically
- Contingency: Revoke token, create new bot

**Risk: Duplicate Notifications**
- Impact: User annoyance, reduced trust
- Probability: Medium
- Mitigation: Robust logging, idempotency checks
- Contingency: Manual cleanup, user apology

### Medium Priority Risks

**Risk: Scheduler Failure**
- Impact: Missed notifications
- Probability: Low
- Mitigation: Monitor job execution, alert on failure
- Contingency: Manual check trigger, fix and restart

**Risk: Database Connection Issues**
- Impact: Bot cannot query deadlines
- Probability: Low
- Mitigation: Connection pooling, retry logic
- Contingency: Restart bot, check database status

### Low Priority Risks

**Risk: Message Formatting Errors**
- Impact: Ugly or unclear messages
- Probability: Low
- Mitigation: Extensive testing, templates
- Contingency: Quick fix and redeploy

**Risk: Unauthorized Command Access**
- Impact: Data exposure
- Probability: Low
- Mitigation: Strict authentication middleware
- Contingency: Review logs, improve auth

---

## Appendix: Code Structure Examples

### Bot Initialization Pattern

```
Bot initialization flow:
1. Load configuration from .env
2. Validate required settings (token, admin_id)
3. Create Bot instance with token
4. Create Dispatcher for routing
5. Register middlewares (auth, logging)
6. Register command handlers
7. Initialize scheduler
8. Start polling or webhook
9. Handle shutdown gracefully
```

### Handler Registration Pattern

```
Command handler structure:
- Define async function with Message parameter
- Add decorator: @router.message(Command("command_name"))
- Implement logic: authenticate, process, respond
- Handle errors with try/except
- Send response via message.answer()
```

### Notification Sending Pattern

```
Notification workflow:
1. Query deadlines from database
2. For each deadline:
   a. Get recipient list (admin + client contacts)
   b. Check notification_logs for existing send
   c. Format message with deadline details
   d. Send via bot.send_message(chat_id, text)
   e. Log result in notification_logs
   f. Handle delivery errors with retry
```

### Database Access Pattern

```
Database interaction:
1. Import models from backend.models
2. Use SQLAlchemy session from backend.database
3. Execute query with proper joins
4. Handle exceptions (connection, integrity)
5. Close session properly
6. Return structured data to handler
```

---

## DETAILED STEP-BY-STEP IMPLEMENTATION PLAN

### Prerequisites Checklist

**Before Starting:**
- [ ] Backend API fully functional and tested
- [ ] Database schema complete with all tables
- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] Telegram bot token obtained from @BotFather
- [ ] Admin Telegram ID identified

---

### STEP 1: Project Setup and Dependencies (30 minutes)

**1.1 Update requirements.txt**

Add to requirements.txt file:
```
aiogram==3.3.0
APScheduler==3.10.4
pytz==2023.3
```

**1.2 Install new dependencies**

Command to execute:
```
pip install -r requirements.txt
```

**1.3 Create bot directory structure**

Create the following directories and files:
```
bot/
├── __init__.py (already exists)
├── main.py
├── config.py
├── handlers/
│   ├── __init__.py
│   ├── common.py
│   ├── admin.py
│   └── deadlines.py
├── services/
│   ├── __init__.py
│   ├── checker.py
│   ├── notifier.py
│   └── formatter.py
├── middlewares/
│   ├── __init__.py
│   ├── auth.py
│   └── logging.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

**1.4 Update .env configuration**

Add to .env file:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_ADMIN_ID=your_telegram_id
NOTIFICATION_CHECK_TIME=09:00
NOTIFICATION_TIMEZONE=Europe/Moscow
NOTIFICATION_RETRY_ATTEMPTS=3
NOTIFICATION_RETRY_DELAY=300
NOTIFICATION_DAYS=14,7,3
```

**Verification:**
- All directories created
- Dependencies installed without errors
- Configuration updated

---

### STEP 2: Bot Configuration Module (20 minutes)

**2.1 Extend backend/config.py**

Task: Add Telegram bot configuration fields to existing Settings class

Fields to add:
- telegram_bot_token: str
- telegram_admin_id: int
- notification_check_time: str (default "09:00")
- notification_timezone: str (default "UTC")
- notification_retry_attempts: int (default 3)
- notification_retry_delay: int (default 300)
- notification_days: str (parse to list)

Validation:
- Ensure telegram_bot_token is not empty
- Ensure telegram_admin_id is positive integer
- Parse notification_days from comma-separated string to list of ints

**2.2 Create bot/config.py**

Task: Create bot-specific configuration wrapper

Content:
- Import Settings from backend.config
- Create get_bot_config() function
- Return bot-related settings
- Add validation for bot token format

**Verification:**
- Settings load without errors
- Bot token validates correctly
- Notification days parse to list: [14, 7, 3]

---

### STEP 3: Database Integration Services (45 minutes)

**3.1 Create bot/services/checker.py**

Task: Implement deadline checking logic

Key Functions:

**get_expiring_deadlines(days: int) -> List[Dict]**
- Query v_expiring_soon view
- Filter by days_until_expiration == days
- Join with clients and deadline_types
- Return list of deadline dictionaries with:
  - deadline_id
  - client_name
  - client_inn
  - deadline_type_name
  - expiration_date
  - days_remaining
  - status (green/yellow/red)

**get_notification_recipients(deadline_id: int) -> List[Dict]**
- Query contacts table by client_id from deadline
- Filter: notifications_enabled = True
- Filter: telegram_id IS NOT NULL
- Add admin_id from config
- Return list with telegram_id and recipient_type

**check_notification_sent(deadline_id: int, days: int, recipient_id: int) -> bool**
- Query notification_logs table
- Check if notification exists for this deadline, days, and recipient
- Return True if already sent, False otherwise

**3.2 Create bot/services/notifier.py**

Task: Implement notification sending logic

Key Functions:

**send_notification(bot, chat_id: int, message: str) -> bool**
- Use bot.send_message()
- Handle Telegram API exceptions
- Return True if sent, False if failed
- Implement retry logic with exponential backoff

**log_notification(deadline_id, recipient_id, days, status, error=None)**
- Insert record into notification_logs table
- Fields: deadline_id, contact_id/admin_flag, notification_type, sent_at, delivery_status, error_message
- Commit transaction

**process_deadline_notifications(bot, days: int) -> Dict**
- Get expiring deadlines for specified days
- For each deadline:
  - Get recipients
  - Check if already notified
  - Format message
  - Send notification
  - Log result
- Return statistics: sent, failed, skipped

**3.3 Create bot/services/formatter.py**

Task: Implement message formatting

Key Functions:

**format_deadline_notification(deadline: Dict, days: int) -> str**
- Add emoji based on urgency (🟢/🟡/🔴)
- Format: "⚠️ Уведомление о дедлайне\n\n"
- Add client info: name, INN
- Add deadline info: type, date, days remaining
- Return formatted string

**format_deadline_list(deadlines: List[Dict]) -> str**
- Format list of deadlines for /list command
- Each entry: [emoji] Client (INN) - Service - Date (X days)
- Separate with dividers
- Return formatted string

**format_statistics(stats: Dict) -> str**
- Format dashboard statistics
- Show counts by status
- Show expiring soon counts
- Return formatted string

**Verification:**
- Database queries execute correctly
- Recipients list includes admin and client contacts
- Duplicate notifications prevented
- Messages formatted properly

---

### STEP 4: Authentication Middleware (20 minutes)

**4.1 Create bot/middlewares/auth.py**

Task: Implement user authentication

Key Components:

**AuthMiddleware class**
- Inherit from BaseMiddleware
- Implement __call__ method
- Extract user Telegram ID from update
- Check if user is admin (compare with TELEGRAM_ADMIN_ID)
- Check if user is client contact (query contacts table)
- Add user_role to handler data: "admin" | "client" | "unknown"
- Add client_id if client user

**is_admin(user_id: int) -> bool**
- Compare user_id with config admin_id
- Return boolean

**get_client_by_telegram_id(telegram_id: int) -> Optional[Dict]**
- Query contacts table
- Join with clients table
- Return client info or None

**Verification:**
- Admin user identified correctly
- Client contacts verified against database
- Unknown users rejected

---

### STEP 5: Bot Handlers Implementation (60 minutes)

**5.1 Create bot/handlers/common.py**

Task: Implement public commands

**/start command handler**
- Welcome message
- Explain bot purpose
- List available commands based on user role
- Check user authorization status

**/help command handler**
- Display command list
- Provide usage examples
- Different help for admin vs client

**5.2 Create bot/handlers/admin.py**

Task: Implement admin-only commands

**/check command handler**
- Verify user is admin (use middleware data)
- Trigger immediate deadline check for all notification days
- Call process_deadline_notifications for each day
- Return statistics: notifications sent, failed, skipped
- Handle errors gracefully

**/status command handler**
- Query dashboard statistics from database
- Use existing v_dashboard_stats view
- Format using formatter.format_statistics
- Send response

**5.3 Create bot/handlers/deadlines.py**

Task: Implement deadline information commands

**/list command handler**
- Get all upcoming deadlines (next 30 days)
- Filter by client if user is client (not admin)
- Format using formatter.format_deadline_list
- Handle pagination if list too long
- Send response

**/today command handler**
- Get deadlines expiring today
- Filter by client if needed
- Format and send

**/week command handler**
- Get deadlines expiring in next 7 days
- Filter by client if needed
- Format and send

**Verification:**
- All commands respond correctly
- Admin commands reject non-admin users
- Client users see only their deadlines
- Error messages user-friendly

---

### STEP 6: Bot Initialization and Routing (30 minutes)

**6.1 Create bot/main.py**

Task: Implement bot initialization and startup

Key Components:

**create_bot() -> Bot**
- Load config
- Create Bot instance with token
- Return bot instance

**create_dispatcher() -> Dispatcher**
- Create Dispatcher instance
- Register middlewares (auth, logging)
- Include routers from handlers
- Return dispatcher

**register_handlers(dp: Dispatcher)**
- Register common handlers (start, help)
- Register admin handlers (check, status)
- Register deadline handlers (list, today, week)
- Set command order and filters

**main() async function**
- Create bot and dispatcher
- Register all handlers
- Start polling
- Handle graceful shutdown
- Close database connections

**Verification:**
- Bot starts without errors
- Responds to /start command
- All commands registered
- Shutdown graceful

---

### STEP 7: Scheduler Integration (30 minutes)

**7.1 Add scheduler to bot/main.py**

Task: Integrate APScheduler for automated checks

Key Components:

**setup_scheduler(bot) -> AsyncIOScheduler**
- Create AsyncIOScheduler instance
- Add cron job for daily check
- Configure timezone from settings
- Schedule: run at notification_check_time
- Job function: scheduled_check(bot)
- Return scheduler

**scheduled_check(bot) async function**
- Log execution start
- Get notification_days from config
- For each day in notification_days:
  - Call process_deadline_notifications(bot, day)
  - Log results
- Handle errors and send admin alert if failed

**Update main() function**
- Initialize scheduler
- Start scheduler
- Keep bot running
- Stop scheduler on shutdown

**Verification:**
- Scheduler starts successfully
- Can trigger manual check with /check
- Scheduled job executes at correct time (test with near-future time)
- Errors logged and reported

---

### STEP 8: Logging and Error Handling (20 minutes)

**8.1 Create bot/middlewares/logging.py**

Task: Implement logging middleware

**LoggingMiddleware class**
- Log all incoming commands
- Log user_id, username, command
- Log execution time
- Log errors with full traceback

**8.2 Configure logging in bot/main.py**

Task: Set up proper logging

- Configure logging format
- Set log level from config
- Create rotating file handler
- Log to: logs/bot.log
- Max file size: 10MB
- Keep 5 backup files

**8.3 Add error handlers**

Task: Handle common errors

- Telegram API errors (rate limit, blocked user)
- Database connection errors
- Unhandled exceptions
- Send admin notification on critical errors

**Verification:**
- All commands logged
- Errors logged with traceback
- Log files rotate correctly
- Admin notified on critical errors

---

### STEP 9: Testing (60 minutes)

**9.1 Unit Tests**

Create tests/test_bot_services.py:

- Test checker.get_expiring_deadlines()
- Test checker.get_notification_recipients()
- Test checker.check_notification_sent()
- Test formatter.format_deadline_notification()
- Test formatter.format_deadline_list()
- Mock database queries

**9.2 Integration Tests**

Create tests/test_bot_integration.py:

- Test notification flow end-to-end
- Test command execution
- Test authentication middleware
- Use test database with sample data

**9.3 Manual Testing**

**Test Bot Commands:**
- Send /start → Should receive welcome
- Send /help → Should see command list
- Send /status (as admin) → Should see statistics
- Send /list → Should see deadlines
- Send /check (as admin) → Should trigger check
- Send /today → Should see today's deadlines
- Send /week → Should see week's deadlines

**Test Notifications:**
- Create test deadline expiring in 14 days
- Run /check command
- Verify notification sent to admin
- Check notification_logs table for entry
- Repeat for 7 and 3 days

**Test Authorization:**
- Try admin commands from non-admin account → Should reject
- Try commands from client contact → Should see only their data
- Try commands from unknown user → Should reject or prompt registration

**Verification:**
- All unit tests pass
- Integration tests pass
- Manual tests successful
- No critical bugs found

---

### STEP 10: Documentation and Deployment Preparation (30 minutes)

**10.1 Update README.md**

Add section: "Telegram Bot Usage"
- How to get bot token
- How to configure .env
- How to start bot
- Available commands
- Troubleshooting

**10.2 Create bot/README.md**

Document:
- Bot architecture
- Module responsibilities
- Configuration options
- Deployment instructions

**10.3 Update requirements.txt**

Ensure all dependencies with versions:
```
aiogram==3.3.0
APScheduler==3.10.4
pytz==2023.3
```

**10.4 Create run script**

Create start_bot.bat (Windows) or start_bot.sh (Linux):
- Activate virtual environment
- Run python -m bot.main
- Handle errors

**Verification:**
- Documentation complete and clear
- Requirements file updated
- Start script works
- Ready for deployment

---

## Implementation Timeline Summary

**Day 1 (4 hours):**
- Steps 1-3: Setup, Config, Database Services
- Deliverable: Core services functional

**Day 2 (4 hours):**
- Steps 4-6: Middleware, Handlers, Bot Init
- Deliverable: Bot responds to commands

**Day 3 (3 hours):**
- Steps 7-8: Scheduler, Logging
- Deliverable: Automated notifications working

**Day 4 (3 hours):**
- Step 9: Testing
- Deliverable: All tests passing

**Day 5 (2 hours):**
- Step 10: Documentation
- Deliverable: Production-ready bot

**Total: 16 hours over 5 days**

---

## Quick Start Commands Reference

**Installation:**
```bash
pip install -r requirements.txt
```

**Configuration:**
```bash
cp .env.example .env
# Edit .env and add TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_ID
```

**Run Bot:**
```bash
python -m bot.main
```

**Run Tests:**
```bash
pytest tests/test_bot_services.py -v
pytest tests/test_bot_integration.py -v
```

**Check Logs:**
```bash
tail -f logs/bot.log
```

---

## Troubleshooting Guide

**Bot doesn't start:**
- Check TELEGRAM_BOT_TOKEN in .env
- Verify token is valid with @BotFather
- Check Python version >= 3.8
- Verify all dependencies installed

**Commands not responding:**
- Check bot polling is active
- Verify handlers registered
- Check logs for errors
- Test with /start command

**Notifications not sending:**
- Verify deadlines exist in database
- Check notification_logs for duplicates
- Verify contacts have telegram_id
- Test with /check command
- Check Telegram API errors in logs

**Database errors:**
- Verify database file exists
- Check file permissions
- Ensure no other process locking database
- Verify SQLAlchemy models match schema

**Scheduler not running:**
- Check scheduler started in main()
- Verify cron expression correct
- Check timezone settings
- Look for scheduler errors in logs
- Test with near-future time first

---

This detailed plan is now ready for implementation! Each step includes specific tasks, verification criteria, and estimated time. Follow the steps sequentially for smooth development.
