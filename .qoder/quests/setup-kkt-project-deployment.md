# KKT Project Multi-Tenant Deployment System Design

## Document Overview

**Purpose**: Define a comprehensive deployment system for KKT (Cash Register Tracking) application that enables automated installation of isolated instances for multiple clients with centralized update distribution.

**Scope**: This design covers the complete workflow from initial VDS provisioning to ongoing update management, including automated setup wizards, billing integration, and production-ready deployment automation.

---

## Business Context

### Problem Statement

Currently, the KKT system is designed for single-instance deployment. To scale the business and serve multiple clients, we need:

1. Automated deployment process for new client instances
2. Complete data and infrastructure isolation between clients
3. Centralized update distribution mechanism
4. Simplified initial setup through interactive wizards
5. Safe testing environment that doesn't affect production

### Solution Overview

A multi-tenant deployment architecture where each client receives:
- Dedicated VDS with isolated PostgreSQL database
- Separate Telegram bot instance
- Independent web application instance
- Update synchronization from a master distribution server (GitHub-based)

### Implementation Strategy

**Phase 1 (MVP - Current Focus):**
- Deployment wizard for automated setup
- Master Distribution Server on existing VDS (kkt-box.net)
- GitHub Releases for version distribution
- Test deployment using copy of current production system
- Manual update process (foundation for future automation)

**Phase 2 (Future):**
- Automated update agent with pull mechanism
- Billing and licensing integration
- Advanced monitoring and analytics

---

## Architecture Overview

### Deployment Model

**Full Isolation Architecture**: Each client operates on a completely isolated infrastructure stack.

```
┌─────────────────────────────────────────────────────────────┐
│                  Master Distribution Server                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ - Master Codebase Repository                           │ │
│  │ - Version Management System                            │ │
│  │ - Update Distribution Service                          │ │
│  │ - Billing & Licensing Service                          │ │
│  │ - Client Registry Database                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Client A VDS    │ │  Client B VDS    │ │  Client N VDS    │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │PostgreSQL  │  │ │  │PostgreSQL  │  │ │  │PostgreSQL  │  │
│  │  Database  │  │ │  │  Database  │  │ │  │  Database  │  │
│  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │Web App     │  │ │  │Web App     │  │ │  │Web App     │  │
│  │(FastAPI)   │  │ │  │(FastAPI)   │  │ │  │(FastAPI)   │  │
│  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │Telegram    │  │ │  │Telegram    │  │ │  │Telegram    │  │
│  │Bot A       │  │ │  │Bot B       │  │ │  │Bot N       │  │
│  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │Update      │  │ │  │Update      │  │ │  │Update      │  │
│  │Agent       │  │ │  │Agent       │  │ │  │Agent       │  │
│  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| Full VDS isolation per client | Guarantees complete data privacy, independent scaling, and compliance with data protection requirements |
| Separate Telegram bot per client | Enables branded experience, independent notification settings, and client-specific command workflows |
| Hybrid update distribution | Critical security patches pushed automatically; feature updates available via pull mechanism with manual approval |
| Web-based setup wizard | Reduces technical barriers for deployment, ensures consistent configuration, and minimizes human error |
| Master distribution server | Centralizes version control, licensing validation, and update distribution |

---

## Deployment Workflow

### Phase 1: Master Distribution Server Setup

This is a one-time setup performed by the KKT development team on existing VDS (kkt-box.net).

#### Master Server Components

**Repository Structure:**

```
kkt-master-distribution/
├── deployment-wizard/
│   ├── backend/              # FastAPI application
│   ├── frontend/             # React/Vue web interface
│   ├── scripts/              # Ansible playbooks
│   └── config.yaml           # Master configuration
├── client-registry/
│   ├── database/             # PostgreSQL schema
│   └── migrations/           # DB migrations
└── docs/
    ├── deployment-guide.md
    └── troubleshooting.md
```

**GitHub Repository Structure:**

```
GitHub: zhurbarv-hub/Qoders
├── releases/
│   ├── v1.0.0/
│   │   ├── kkt-app.tar.gz
│   │   ├── CHANGELOG.md
│   │   └── checksums.txt
│   └── v1.1.0/
│       ├── kkt-app.tar.gz
│       ├── CHANGELOG.md
│       ├── checksums.txt
│       └── migration-scripts/
└── tags: v1.0.0, v1.1.0, ...
```

**Services Running on Master (kkt-box.net):**

1. **Deployment Wizard Backend**: API service for interactive setup process (port 8100)
2. **Deployment Wizard Frontend**: Web UI for deployment (served via Nginx)
3. **Client Registry Database**: PostgreSQL database tracking deployed instances
4. **Existing Production Instance**: Current working system (untouched, runs on port 8000)

**Master Server Current State:**

- Host: kkt-box.net (Ubuntu 24.04)
- PostgreSQL 14+ already installed
- Nginx with SSL already configured
- Current production: Web app (port 8000) + Bot + Database
- Available resources for Master services

**Port Allocation:**

| Service | Port | Purpose |
|---------|------|----------|
| Production Web App | 8000 | Existing working system (DO NOT TOUCH) |
| Production Bot | N/A | Existing Telegram bot |
| Deployment Wizard API | 8100 | New master distribution backend |
| Deployment Wizard Web | 443 | Nginx serves at /deploy path |
| Client Registry DB | 5432 | PostgreSQL (separate database: kkt_master_registry) |

---

### Phase 2: Test Deployment Preparation

**CRITICAL: Creating Safe Test Environment**

Before deploying to real clients, we create a test copy of current production to validate the deployment system.

#### Step 2.1: Test Environment Setup

**Test Deployment Target:**

Option A: Same VDS (kkt-box.net) with isolated services:
- Separate PostgreSQL database: `kkt_test_instance`
- Web app on different port: 8200
- Separate Telegram bot (new test bot)
- Separate systemd services: `kkt-test-web.service`, `kkt-test-bot.service`
- Subdomain or path: `test.kkt-box.net` or `kkt-box.net/test`

Option B: Separate test VDS:
- Completely isolated test environment
- Safe for breaking changes
- Recommended if resources allow

**Test Deployment Goals:**

1. Validate deployment wizard works end-to-end
2. Test that production system remains unaffected
3. Verify isolation between instances
4. Test update mechanism (manual for MVP)
5. Document any issues for production deployments

#### Step 2.2: Pre-Deployment Preparation (Real Clients)

**Inputs Required:**

1. Client VDS information:
   - IP address
   - SSH access credentials (root or sudo user)
   - Domain name (for HTTPS setup)

2. Telegram Bot creation:
   - Client must create bot via @BotFather
   - Obtain bot token
   - Optionally configure bot name/description

3. Client business information:
   - Company name
   - Primary contact person details

**Pre-deployment Checklist:**

- [ ] VDS provisioned with Ubuntu 22.04 or 24.04 LTS
- [ ] SSH access confirmed
- [ ] Domain DNS pointing to VDS IP
- [ ] Telegram bot token obtained
- [ ] Deployment wizard tested on test instance

---

#### Step 2.3: Interactive Deployment Wizard

The wizard can be accessed via two methods:

**Method A: Web-Based Wizard (Recommended)**

Access deployment wizard at: `https://kkt-box.net/deploy`

Two access modes:
1. **Self-Service Mode**: Client enters deployment details themselves
2. **Assisted Mode**: You (admin) guide client through process or deploy on their behalf

**Method B: CLI-Based Wizard**

SSH into target VDS and run:
```bash
curl -sSL https://kkt-box.net/deploy/install.sh | bash
```

**Access Control:**

- Web interface is publicly accessible
- Deployment execution requires authentication (admin credentials or one-time deployment token)
- Each deployment creates audit log in Client Registry

#### Wizard Workflow

```mermaid
flowchart TD
    Start([Start Deployment Wizard]) --> Welcome[Display Welcome Screen]
    Welcome --> ModeSelect{Select Mode}
    ModeSelect -->|New Deployment| VDSInfo[Enter VDS Connection Info]
    ModeSelect -->|Test Deployment| TestMode[Use Test Configuration]
    TestMode --> ConfirmTest{Deploy to kkt-box.net?}
    ConfirmTest -->|Yes| SetTestParams[Set Test Parameters:<br/>Port 8200, test DB]
    ConfirmTest -->|No| VDSInfo
    SetTestParams --> AdminSetup
    VDSInfo --> TestConnection{Test SSH Connection}
    TestConnection -->|Failed| VDSInfo
    TestConnection -->|Success| AdminSetup[Setup Initial Admin User]
    AdminSetup --> CollectAdminData[Collect Admin Data:<br/>- Full Name<br/>- Email<br/>- Phone<br/>- Company Name]
    CollectAdminData --> TelegramBot[Configure Telegram Bot]
    TelegramBot --> BotToken[Enter Bot Token from @BotFather]
    BotToken --> ValidateBot{Validate Bot Token}
    ValidateBot -->|Invalid| BotToken
    ValidateBot -->|Valid| WebhookSetup[Auto-configure Webhook]
    WebhookSetup --> AdminTelegram[Add Admin Telegram IDs]
    AdminTelegram --> AdminIDs[Enter Admin Telegram IDs<br/>Multiple IDs separated by comma]
    AdminIDs --> SystemSettings[Configure System Settings]
    SystemSettings --> NotificationTime[Set Notification Time]
    NotificationTime --> NotificationDays[Set Alert Thresholds<br/>Default: 14, 7, 3 days]
    NotificationDays --> Timezone[Select Timezone]
    Timezone --> Review[Review Configuration]
    Review --> Confirm{Confirm Settings?}
    Confirm -->|No| AdminSetup
    Confirm -->|Yes| StartDeploy[Begin Automated Deployment]
    StartDeploy --> InstallSystem[Install System Components]
    InstallSystem --> SetupDB[Setup PostgreSQL Database]
    SetupDB --> DeployApp[Deploy Application]
    DeployApp --> ConfigServices[Configure systemd Services]
    ConfigServices --> SetupNginx[Setup Nginx + SSL]
    SetupNginx --> InitDB[Initialize Database Schema]
    InitDB --> CreateAdmin[Create Admin User in DB]
    CreateAdmin --> StartServices[Start All Services]
    StartServices --> HealthCheck{Health Check}
    HealthCheck -->|Failed| ShowLogs[Display Error Logs]
    ShowLogs --> ManualFix[Manual Intervention Required]
    HealthCheck -->|Passed| RegisterClient[Register Instance in Master]
    RegisterClient --> Success([Deployment Complete])
```

---

#### Step 2.3: Automated Deployment Process

Once configuration is confirmed, the wizard executes the following automated steps:

**Phase A: System Environment Setup**

Actions performed:
- Update operating system packages
- Install Python 3.11+
- Install PostgreSQL 14+
- Install Nginx web server
- Install Certbot for SSL certificates
- Configure UFW firewall rules

Expected duration: 10-15 minutes

**Phase B: Database Initialization**

Actions performed:
- Create PostgreSQL database with name pattern: `kkt_client_{CLIENT_ID}`
- Create database user with strong auto-generated password
- Apply database schema from master distribution
- Insert initial data (deadline types, OFD providers)
- Create database backup script and schedule it via cron

Expected duration: 5 minutes

**Phase C: Application Deployment**

Actions performed:
- Create application user: `kktapp`
- Download application release from GitHub (latest or specified version)
- Extract release package: `kkt-app.tar.gz`
- Create Python virtual environment
- Install all dependencies from requirements.txt
- Generate `.env` configuration file with all collected parameters
- Set appropriate file permissions (`.env` = 600)
- Create log directories: `/var/log/kkt-system/`
- Create version tracking file: `/home/kktapp/kkt-system/.version`

Expected duration: 10 minutes

**Download Process:**

```
1. Fetch latest release from GitHub API:
   GET https://api.github.com/repos/zhurbarv-hub/Qoders/releases/latest

2. Download release asset:
   curl -L -o kkt-app.tar.gz {asset_download_url}

3. Verify checksum:
   sha256sum -c checksums.txt

4. Extract:
   tar -xzf kkt-app.tar.gz -C /home/kktapp/kkt-system
```

**Phase D: Service Configuration**

Actions performed:
- Create systemd service file: `kkt-web.service`
- Create systemd service file: `kkt-bot.service`
- Enable auto-start on boot
- Start both services
- Verify service status

Expected duration: 2 minutes

**Phase E: Web Server Setup**

Actions performed:
- Generate Nginx configuration for the domain
- Configure reverse proxy to FastAPI application
- Request and install SSL certificate via Let's Encrypt
- Configure automatic certificate renewal
- Enable HTTPS with security headers
- Test Nginx configuration

Expected duration: 5 minutes

**Phase F: Telegram Bot Configuration**

Actions performed:
- Set Telegram webhook to: `https://{DOMAIN}/api/telegram/webhook`
- Verify webhook is accessible (Telegram performs callback test)
- Send test notification to admin Telegram IDs
- Confirm bot responds to `/start` command

Expected duration: 2 minutes

**Phase G: Version Tracking**

Actions performed:
- Record deployed version in `.version` file
- Register instance in Master Client Registry
- Create initial deployment history record
- Set up health check reporting (if enabled)

Expected duration: 1 minute

---

#### Step 2.4: Initial Admin User Creation

During deployment, the wizard creates the first admin user in the `users` table:

**User Data Structure:**

| Field | Value | Source |
|-------|-------|--------|
| email | Admin email | Wizard input |
| password_hash | Bcrypt hashed password | Auto-generated or wizard input |
| full_name | Admin full name | Wizard input |
| role | `admin` | Default |
| phone | Admin phone | Wizard input |
| company_name | Company name | Wizard input |
| telegram_id | Admin Telegram ID | Wizard input |
| is_active | `true` | Default |

**Credential Delivery:**

After successful deployment, the wizard provides:
- Web interface URL: `https://{DOMAIN}`
- Admin login credentials (email + password)
- Telegram bot link: `t.me/{BOT_USERNAME}`
- Connection instructions for admins

These credentials are:
1. Displayed in wizard completion screen
2. Sent via email to admin email address
3. Stored encrypted in master server client registry

---

#### Step 2.5: Post-Deployment Validation

Automated health checks performed:

| Check | Validation Method | Expected Result |
|-------|-------------------|-----------------|
| PostgreSQL Status | `systemctl status postgresql` | Active (running) |
| Web Service Status | `systemctl status kkt-web.service` | Active (running) |
| Bot Service Status | `systemctl status kkt-bot.service` | Active (running) |
| Nginx Status | `systemctl status nginx` | Active (running) |
| Web Health Endpoint | `curl https://{DOMAIN}/health` | HTTP 200 + `{"status":"ok"}` |
| SSL Certificate | `openssl s_client -connect {DOMAIN}:443` | Valid certificate chain |
| Database Connection | Query `SELECT 1` via application | Success |
| Telegram Webhook | Check via Telegram API | Webhook active |
| Admin Login | Attempt login with generated credentials | Authentication successful |

If any check fails, the wizard:
1. Captures detailed logs
2. Attempts automatic remediation for common issues
3. Provides manual troubleshooting steps if auto-fix fails
4. Sends failure report to master server for support team review

---

### Phase 3: GitHub-Based Distribution Repository

#### Repository Structure

GitHub repository (zhurbarv-hub/Qoders) serves as the single source of truth for all deployable code.

**Development Repository Organization:**

```
zhurbarv-hub/Qoders/
├── README.md
├── CHANGELOG.md
├── VERSION
├── .github/
│   └── workflows/
│       └── release.yml          # Automated release builder
├── backend/
├── bot/
├── web/
├── database/
├── deployment/
├── requirements.txt
└── requirements-web.txt
```

**GitHub Releases Structure:**

Each release tag (e.g., v1.0.0) includes:
- `kkt-app.tar.gz` - Complete application package
- `checksums.txt` - SHA256 checksums for verification
- `CHANGELOG.md` - Release notes
- `migration-scripts.tar.gz` - Database migrations (if needed)

**Release Assets Naming:**
```
Release: v1.0.0
  ├── kkt-app-v1.0.0.tar.gz
  ├── checksums.txt
  └── Source code (zip)
  └── Source code (tar.gz)
```

#### Release Packaging Process

**Step 1: Code Finalization**

Development team completes feature development, testing, and code review in the main development repository.

**Step 2: Version Tagging**

1. Update VERSION file with semantic version (e.g., `1.1.0`)
2. Update CHANGELOG.md with all changes in this release
3. Create Git tag: `v1.1.0`
4. Push tag to GitHub: `git push origin v1.1.0`

**Step 3: Automated Release Creation (GitHub Actions)**

GitHub Actions workflow triggered by tag push:

```yaml
Workflow: .github/workflows/release.yml
Trigger: Tag push matching v*.*.*

Steps:
1. Checkout tagged version
2. Remove development files (tests, docs, temp scripts)
3. Create release package:
   tar -czf kkt-app-v1.1.0.tar.gz \
     backend/ bot/ web/ database/ deployment/ \
     requirements.txt requirements-web.txt .env.example
4. Generate SHA256 checksum
5. Create GitHub Release
6. Upload kkt-app-v1.1.0.tar.gz as release asset
7. Upload checksums.txt as release asset
8. If migrations exist, package and upload migration-scripts.tar.gz
```

**Step 4: Release Notification**

1. GitHub Release is created automatically
2. Manual step (for now): Update Client Registry with new version info
3. Optionally: Send email notification to clients about new version
4. Clients can check for updates via web interface

**Manual Release Creation (if GitHub Actions not used):**

```bash
# Local script: scripts/create-release.sh
#!/bin/bash
VERSION=$1

# Create clean package
tar -czf kkt-app-v${VERSION}.tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='test_*.py' \
  backend/ bot/ web/ database/ deployment/ \
  requirements.txt requirements-web.txt .env.example

# Generate checksum
sha256sum kkt-app-v${VERSION}.tar.gz > checksums.txt

# Create GitHub release via CLI
gh release create v${VERSION} \
  kkt-app-v${VERSION}.tar.gz \
  checksums.txt \
  --title "Release v${VERSION}" \
  --notes-file CHANGELOG.md
```

---

#### Update Manifest Structure

Each release includes a JSON manifest describing the update:

```
{
  "version": "1.1.0",
  "release_date": "2026-01-10T12:00:00Z",
  "severity": "minor",
  "requires_restart": true,
  "database_migration": true,
  "breaking_changes": false,
  "download_url": "https://releases.kkt-master.com/v1.1.0/kkt-app.tar.gz",
  "checksum": "abc123def456...",
  "changelog": {
    "added": [
      "New dashboard statistics widget",
      "Export deadlines to Excel"
    ],
    "fixed": [
      "Telegram notification retry logic",
      "Date calculation bug in reports"
    ],
    "changed": [
      "Improved UI for client management"
    ],
    "security": []
  },
  "migration_steps": [
    {
      "type": "sql",
      "file": "migrations/011_add_export_settings.sql",
      "description": "Add export settings table"
    }
  ],
  "rollback_supported": true,
  "minimum_version": "1.0.0"
}
```

**Severity Levels:**

| Severity | Description | Auto-Deploy | Client Action Required |
|----------|-------------|-------------|------------------------|
| critical | Security vulnerability or data loss bug | Yes (forced) | None - automatic |
| major | Important bug fixes or significant features | No | Review and approve |
| minor | Feature enhancements, minor bug fixes | No | Optional update |
| patch | Cosmetic changes, documentation | No | Optional update |

---

### Phase 4: Update Mechanism (MVP - Manual Process)

**Note:** For Phase 1 (MVP), updates are **manual** - no automated update agent. This provides:
- Simple, reliable foundation
- Full control over when updates happen
- Time to perfect deployment before automation
- Basis for future automated update system

#### Manual Update Process

**Check for Updates:**

Admins check for updates via:
1. **Web Interface**: Settings → System Updates → "Check for Updates" button
2. **Command Line** (on client VDS):
   ```bash
   cd /home/kktapp/kkt-system
   ./scripts/check-updates.sh
   ```

**Update Check Script:**

```bash
# scripts/check-updates.sh
#!/bin/bash

CURRENT_VERSION=$(cat /home/kktapp/kkt-system/.version)

# Fetch latest release from GitHub API
LATEST_VERSION=$(curl -s https://api.github.com/repos/zhurbarv-hub/Qoders/releases/latest | \
  grep '"tag_name":' | \
  sed -E 's/.*"([^"]+)".*/\1/')

if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
  echo "Update available: $CURRENT_VERSION → $LATEST_VERSION"
  echo "Run: ./scripts/apply-update.sh to install"
else
  echo "System is up to date: $CURRENT_VERSION"
fi
```

**Apply Update Script:**

```bash
# scripts/apply-update.sh
#!/bin/bash
set -e

echo "Creating backup..."
./scripts/backup-system.sh

echo "Downloading latest release..."
LATEST_URL=$(curl -s https://api.github.com/repos/zhurbarv-hub/Qoders/releases/latest | \
  grep 'browser_download_url.*kkt-app.*tar.gz' | \
  cut -d '"' -f 4)

curl -L -o /tmp/kkt-app-update.tar.gz "$LATEST_URL"

echo "Stopping services..."
sudo systemctl stop kkt-web kkt-bot

echo "Extracting update..."
tar -xzf /tmp/kkt-app-update.tar.gz -C /home/kktapp/kkt-system-new/

echo "Applying update..."
rsync -av --exclude='.env' /home/kktapp/kkt-system-new/ /home/kktapp/kkt-system/

echo "Starting services..."
sudo systemctl start kkt-web kkt-bot

echo "Verifying health..."
sleep 5
curl -f http://localhost:8000/health || { echo "Health check failed! Rolling back..."; ./scripts/rollback.sh; exit 1; }

echo "Update completed successfully!"
```

#### Future: Automated Update Agent (Phase 2)

After MVP is stable, implement automated update agent:

**Simple Cron-Based Agent:**

```bash
# Cron job runs daily at 3 AM
0 3 * * * /home/kktapp/kkt-system/scripts/auto-update.sh
```

**Auto-Update Script (Phase 2):**
```bash
# scripts/auto-update.sh
#!/bin/bash

# Check if updates enabled
if [ "$(cat /home/kktapp/.kkt-auto-update)" != "enabled" ]; then
  exit 0
fi

# Check for updates
./scripts/check-updates.sh | grep "Update available" || exit 0

# Apply update
./scripts/apply-update.sh

# Send notification
./scripts/notify-update-complete.sh
```

---

#### Update Workflow

```mermaid
sequenceDiagram
    participant Agent as Update Agent<br/>(Client VDS)
    participant Master as Master Distribution Server
    participant App as KKT Application
    participant DB as PostgreSQL Database
    
    loop Every Check Interval
        Agent->>Master: Check for updates (client_id, current_version)
        Master->>Agent: Return available updates + manifest
        
        alt Critical Update Available
            Agent->>Agent: Auto-approve for installation
        else Non-Critical Update
            Agent->>Agent: Send notification to admin
            Agent->>Agent: Wait for manual approval
        end
        
        alt Update Approved
            Agent->>Agent: Create backup (database + code)
            Agent->>Master: Download update package
            Master->>Agent: Send kkt-app.tar.gz
            Agent->>Agent: Verify checksum
            
            alt Database Migration Required
                Agent->>App: Stop application services
                App->>Agent: Services stopped
                Agent->>DB: Apply migration scripts
                DB->>Agent: Migration complete
            end
            
            Agent->>Agent: Extract new code
            Agent->>Agent: Update configuration
            Agent->>App: Restart application services
            App->>Agent: Services started
            
            Agent->>App: Perform health checks
            
            alt Health Checks Pass
                App->>Agent: All checks OK
                Agent->>Master: Report update success
                Master->>Agent: Acknowledge
            else Health Checks Fail
                App->>Agent: Service unhealthy
                Agent->>Agent: Initiate rollback
                Agent->>DB: Restore database backup
                Agent->>Agent: Restore previous code version
                Agent->>App: Restart with old version
                Agent->>Master: Report update failure + logs
            end
        end
    end
```

---

#### Manual Update Process (via Web Interface)

For non-critical updates, admins can manage updates through the web dashboard:

**UI Workflow:**

1. **Updates Available Notification**
   - Dashboard displays badge: "1 Update Available"
   - Admin navigates to Settings → System Updates

2. **Update Review Screen**
   - Display version information
   - Show changelog (added, fixed, changed features)
   - Indicate if database migration required
   - Show estimated downtime
   - Display rollback availability

3. **Update Approval**
   - Admin clicks "Review Update"
   - Option to schedule update (immediate or specific time)
   - Confirm understanding of downtime
   - Click "Apply Update"

4. **Update Progress**
   - Real-time progress bar
   - Step-by-step status updates:
     - Creating backup...
     - Stopping services...
     - Downloading update...
     - Applying database migrations...
     - Installing new version...
     - Starting services...
     - Running health checks...

5. **Update Completion**
   - Success: "Update completed successfully! Version 1.1.0 is now active."
   - Failure: "Update failed. System rolled back to version 1.0.0. Error details: [...]"

---

#### Rollback Mechanism

If an update fails or causes issues, the system can roll back to the previous version.

**Rollback Triggers:**

- Health check failure after update
- Service start failure
- Database migration failure
- Manual rollback request by admin

**Rollback Process:**

1. Stop all application services
2. Restore database from pre-update backup
3. Restore previous application code version
4. Restore previous `.env` configuration
5. Restart services
6. Perform health checks
7. Report rollback status to master server

**Rollback Limitations:**

- Rollback window: 7 days after update
- Database migrations with irreversible changes (e.g., data deletion) may not support rollback
- Update manifest indicates if rollback is supported

---

### Phase 5: Client Registry Database

**Purpose:** Track all deployed instances, versions, and deployment history.

#### Database Schema

**Database:** `kkt_master_registry` (PostgreSQL on kkt-box.net)

**Table: `deployed_instances`**

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique instance ID |
| instance_name | VARCHAR(100) | Client-friendly name |
| client_company | VARCHAR(255) | Company name |
| vds_ip | VARCHAR(45) | VDS IP address |
| domain | VARCHAR(255) | Domain name |
| deployed_version | VARCHAR(20) | Current installed version |
| deployed_at | TIMESTAMP | Initial deployment date |
| last_health_check | TIMESTAMP | Last successful health check |
| status | VARCHAR(20) | active, inactive, error |
| notes | TEXT | Additional information |

**Table: `deployment_history`**

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique record ID |
| instance_id | INTEGER | FK to deployed_instances |
| action | VARCHAR(50) | deploy, update, rollback |
| from_version | VARCHAR(20) | Previous version (for updates) |
| to_version | VARCHAR(20) | New version |
| initiated_by | VARCHAR(100) | Admin email or "auto" |
| started_at | TIMESTAMP | Action start time |
| completed_at | TIMESTAMP | Action completion time |
| status | VARCHAR(20) | success, failed, in_progress |
| error_log | TEXT | Error details if failed |

**Table: `admin_users`**

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique admin ID |
| email | VARCHAR(255) | Admin email (unique) |
| password_hash | VARCHAR(255) | Bcrypt hashed password |
| full_name | VARCHAR(255) | Admin full name |
| role | VARCHAR(20) | superadmin, deployer |
| is_active | BOOLEAN | Account active status |
| created_at | TIMESTAMP | Account creation date |

#### Client Registry API

**Endpoints:**

```
GET  /api/registry/instances              # List all instances
GET  /api/registry/instances/{id}         # Get instance details
POST /api/registry/instances              # Register new instance
PUT  /api/registry/instances/{id}         # Update instance info
GET  /api/registry/instances/{id}/history # Get deployment history
POST /api/registry/instances/{id}/health  # Report health status
```

### Phase 6: Billing and Licensing System (Future - Phase 2+)

**Note:** Billing system is postponed to future phase. For MVP:
- No license validation
- No payment processing
- All deployments are "free" for testing
- Foundation prepared for future integration

#### Licensing Model

**Subscription-Based Model:**

Each client instance requires an active license to operate. License validation occurs:
- During initial deployment
- On every application startup
- Periodically during runtime (every 24 hours)

**License Tiers:**

| Tier | Max Clients | Max Users | Max Cash Registers | Price (Monthly) |
|------|-------------|-----------|-------------------|-----------------|
| Starter | 50 | 3 | Unlimited | $49 |
| Professional | 200 | 10 | Unlimited | $99 |
| Enterprise | Unlimited | Unlimited | Unlimited | $299 |

**Additional Features by Tier:**

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| Telegram Bot | ✓ | ✓ | ✓ |
| Email Notifications | ✗ | ✓ | ✓ |
| API Access | ✗ | ✓ | ✓ |
| Custom Branding | ✗ | ✗ | ✓ |
| Priority Support | ✗ | ✗ | ✓ |
| On-Premise Hosting | ✗ | ✗ | ✓ |

---

#### License Validation Architecture

**Components:**

1. **Master License Server**: Centralized service managing all licenses
2. **Client License Module**: Embedded in each client instance
3. **License Database**: Stores license records and validation history

**License Validation Flow:**

```mermaid
sequenceDiagram
    participant App as KKT Application
    participant LM as License Module
    participant LS as License Server (Master)
    participant DB as License Database
    
    App->>LM: Application startup
    LM->>LM: Read local license cache
    
    alt License cached and valid
        LM->>LS: Validate license (license_key, client_id)
        LS->>DB: Query license record
        DB->>LS: Return license data
        
        alt License Valid
            LS->>LM: License valid + expiration date
            LM->>LM: Update local cache
            LM->>App: Proceed with startup
        else License Expired
            LS->>LM: License expired
            LM->>App: Block application + display renewal notice
        else License Revoked
            LS->>LM: License revoked
            LM->>App: Block application + display violation message
        end
    else No cached license
        LM->>App: Block application + display activation required
    end
```

**Grace Period:**

If license server is unreachable, the application uses cached license validation for up to 7 days. After grace period, application requires manual license refresh.

---

#### License Enforcement

**Enforcement Points:**

1. **Application Startup**: Validate license before initializing services
2. **User Login**: Check license status before allowing authentication
3. **Resource Limits**: Enforce tier limits (max clients, users, etc.)
4. **Feature Access**: Disable features not included in current tier

**Soft Limits vs Hard Limits:**

| Limit Type | Behavior | Example |
|------------|----------|---------|
| Soft Limit | Warning displayed, functionality continues | Approaching max clients (90% of limit) |
| Hard Limit | Functionality blocked | Max clients reached - cannot create new |

**License Expiration Notifications:**

- 30 days before expiration: Email notification
- 14 days before expiration: Email + in-app banner
- 7 days before expiration: Email + prominent in-app warning
- 1 day before expiration: Email + blocking modal on login
- After expiration: Application blocked, display renewal instructions

---

#### Billing Integration Options

The system supports integration with multiple billing providers:

**Option 1: Stripe Integration**

- Subscription management via Stripe Billing
- Automatic payment processing
- Webhook notifications for subscription events (created, renewed, canceled)
- Customer portal for self-service billing management

**Option 2: Manual Billing**

- Invoice generation in master system
- Payment tracking via admin panel
- Manual license activation after payment confirmation

**Option 3: Reseller Model**

- Resellers purchase license keys in bulk
- Resellers manage their own billing relationships
- Master system tracks license usage and reseller attribution

---

## Test Deployment Workflow

### Creating Test Instance on Production VDS

**Goal:** Deploy a copy of current production system to test deployment wizard without affecting live system.

#### Test Instance Specifications

**Isolation Strategy:**

| Component | Production | Test Instance |
|-----------|-----------|---------------|
| Database | `kkt_production` | `kkt_test_instance` |
| Web Service | `kkt-web.service` (port 8000) | `kkt-test-web.service` (port 8200) |
| Bot Service | `kkt-bot.service` | `kkt-test-bot.service` |
| Application Directory | `/home/kktapp/kkt-system` | `/home/kktapp/kkt-test-system` |
| Nginx Location | `location /` | `location /test/` |
| Domain | `kkt-box.net` | `kkt-box.net/test` or `test.kkt-box.net` |
| Telegram Bot | Production bot | New test bot (create via @BotFather) |
| .env file | `/home/kktapp/kkt-system/.env` | `/home/kktapp/kkt-test-system/.env` |

#### Test Deployment Steps

**Step 1: Prepare Test Bot**

1. Create new bot via @BotFather:
   - Send `/newbot` to @BotFather
   - Name: "KKT Test Bot" (or similar)
   - Get bot token

2. Note test admin Telegram IDs

**Step 2: Run Deployment Wizard in Test Mode**

1. Access wizard: `https://kkt-box.net/deploy`
2. Select "Test Deployment" mode
3. Wizard auto-fills:
   - Target: localhost (kkt-box.net)
   - Port: 8200
   - Database: kkt_test_instance
   - Directory: /home/kktapp/kkt-test-system
4. Enter test bot token
5. Enter admin details (can reuse production admin info)
6. Confirm and deploy

**Step 3: Verify Test Instance**

1. Check services running:
   ```bash
   systemctl status kkt-test-web.service
   systemctl status kkt-test-bot.service
   ```

2. Access test web interface:
   - URL: `https://kkt-box.net/test` (if using path)
   - Or: `https://test.kkt-box.net` (if using subdomain)

3. Test Telegram bot:
   - Send `/start` to test bot
   - Verify response

4. Verify production unaffected:
   - Access: `https://kkt-box.net`
   - Check production bot still works
   - Verify production database unchanged

**Step 4: Test Update Process**

1. Create a minor code change in test instance
2. Create new GitHub release (e.g., v1.0.1-test)
3. Run manual update on test instance:
   ```bash
   cd /home/kktapp/kkt-test-system
   ./scripts/check-updates.sh
   ./scripts/apply-update.sh
   ```
4. Verify update successful
5. Verify rollback works if needed

**Step 5: Clean Up (After Testing)**

Once satisfied with deployment system:
```bash
# Stop test services
sudo systemctl stop kkt-test-web kkt-test-bot
sudo systemctl disable kkt-test-web kkt-test-bot

# Remove test systemd services
sudo rm /etc/systemd/system/kkt-test-*.service
sudo systemctl daemon-reload

# Optionally remove test database
sudo -u postgres psql -c "DROP DATABASE kkt_test_instance;"

# Optionally remove test files
rm -rf /home/kktapp/kkt-test-system
```

## Deployment Wizard Configuration

### Initial Setup Wizard Flow

#### Step 1: Welcome and Mode Selection

**Screen Elements:**

- Welcome message and KKT system description
- Deployment mode selection:
  - **Production Deployment**: Deploy to client VDS
  - **Test Deployment**: Deploy test instance on kkt-box.net (for development/testing)
- Authentication:
  - Admin login (username/password)
  - Or: One-time deployment token (for client self-service)

**Validation:**

- Valid admin credentials or deployment token required
- Test deployment only available to admins

**Data Collected:**

- Deployment mode selection
- Authentication credentials

---

#### Step 2: Administrator Account Setup

**Screen Elements:**

- Section title: "Create Administrator Account"
- Input fields:
  - Full Name (required)
  - Email Address (required, validated format)
  - Phone Number (required, validated format)
  - Company Name (required)
- Password generation options:
  - Auto-generate strong password (recommended)
  - Manually enter password (must meet complexity requirements)
- Display generated password with copy button

**Validation Rules:**

- Email must be valid format and unique
- Phone number must be valid format (international format recommended)
- If manual password: minimum 12 characters, must include uppercase, lowercase, number, special character
- All fields are required

**Data Collected:**

- Administrator full name
- Administrator email
- Administrator phone number
- Company name
- Password (hashed before storage)

---

#### Step 3: Telegram Bot Configuration

**Screen Elements:**

- Instructions: "Create a new bot via @BotFather in Telegram"
- Link to BotFather: `t.me/BotFather`
- Step-by-step guide:
  1. Open BotFather in Telegram
  2. Send `/newbot` command
  3. Follow instructions to name your bot
  4. Copy the bot token provided
- Bot token input field (validated)
- "Validate Bot" button

**Bot Token Validation:**

- Format: `[0-9]+:[A-Za-z0-9_-]{35}`
- Test API call to Telegram to verify token is active
- Display bot username after validation

**Data Collected:**

- Telegram bot token

---

#### Step 4: Administrator Telegram IDs

**Screen Elements:**

- Instructions: "Add Telegram IDs of administrators who will receive notifications"
- How to find Telegram ID:
  - Use bot `@userinfobot`
  - Send any message to get your Telegram ID
- Input field for Telegram IDs (comma-separated for multiple)
- "Add Another Admin" button
- List of added admin IDs with remove option

**Validation:**

- Each Telegram ID must be numeric
- At least one admin Telegram ID required
- Optionally verify IDs by sending test message to each

**Data Collected:**

- List of administrator Telegram IDs

---

#### Step 5: System Settings

**Screen Elements:**

- **Notification Time**:
  - Time picker for daily notification check
  - Default: 09:00

- **Timezone**:
  - Dropdown list of timezones
  - Auto-detect timezone from browser
  - Default: Europe/Moscow

- **Alert Thresholds**:
  - Days before expiration to send alerts
  - Default values: 14, 7, 3 days
  - Customizable (comma-separated list)

- **Backup Schedule**:
  - Automatic daily backup time
  - Default: 03:00
  - Retention period (default: 7 days)

**Data Collected:**

- Notification check time
- System timezone
- Alert threshold days
- Backup schedule settings

---

#### Step 6: Review and Confirm

**Screen Elements:**

- Summary of all collected information:
  - License tier and expiration
  - Administrator details
  - Telegram bot information
  - System settings
- "Edit" buttons next to each section to return and modify
- Checkbox: "I confirm all information is correct"
- "Begin Deployment" button (enabled only after confirmation)

**Data Validation:**

- Final validation of all inputs
- Check license is still valid
- Verify bot token is still active
- Ensure no data integrity issues

---

#### Step 7: Deployment Progress

**Screen Elements:**

- Progress bar (0-100%)
- Current step indicator
- Live log output (scrollable terminal-style display)
- Estimated time remaining
- **Important**: Show clear message that production system is not affected

**Progress Steps:**

1. Connecting to target server... (0-5%)
2. Installing system packages... (5-25%)
3. Setting up database... (25-40%)
4. Downloading application from GitHub... (40-55%)
5. Deploying application... (55-75%)
6. Configuring services... (75-85%)
7. Setting up web server and SSL... (85-95%)
8. Running health checks... (95-98%)
9. Registering instance in Client Registry... (98-100%)

**Error Handling:**

- If any step fails:
  - Pause deployment
  - Display detailed error message
  - Offer options:
    - Retry step
    - View full logs
    - Contact support
    - Rollback deployment (if partial installation)

**For Test Deployment:**
- Additional check: Verify production services still running
- Show real-time comparison: Production vs Test status

---

#### Step 8: Deployment Complete

**Screen Elements:**

- Success message: "Deployment Completed Successfully!"
- Instance information card:
  - Instance ID: `INST-{timestamp}`
  - Web Interface URL: `https://{domain}`
  - Admin Email: `{admin_email}`
  - Admin Password: `{generated_password}`
  - Copy button for credentials
- Telegram bot link: `t.me/{bot_username}`
- Version deployed: `v1.0.0` (from GitHub release)
- Next steps checklist:
  - [ ] Login to web interface
  - [ ] Change admin password (if auto-generated)
  - [ ] Add first client
  - [ ] Test Telegram bot by sending `/start`
  - [ ] Bookmark Settings → System Updates for future updates
- "Email credentials to admin" button
- "Download deployment report as PDF" button
- "Go to Dashboard" button (opens new instance)
- "Deploy Another Instance" button

**Post-Deployment Actions:**

- Send welcome email with credentials
- Register instance in Client Registry database
- Record deployment history
- Send notification to KKT admin team
- If test deployment: Display comparison with production

**Test Deployment Specific:**
- Display test instance access info
- Show production system status (confirm unaffected)
- Provide cleanup script for later removal

---

## Technical Implementation Details

### Deployment Wizard Technology Stack

**Frontend:**

- Framework: React.js or Vue.js
- UI Components: Material-UI or Ant Design
- State Management: Redux or Vuex
- Form Validation: Formik + Yup (React) or Vuelidate (Vue)

**Backend:**

- Framework: FastAPI (Python)
- Task Queue: Celery with Redis
- Real-time Updates: WebSocket (Socket.IO or FastAPI WebSocket)
- SSH Operations: Paramiko library
- Encryption: cryptography library for secure credential storage

**Deployment Execution:**

- Ansible playbooks for remote server configuration
- Shell scripts for specific installation steps
- Progress tracking via database + WebSocket broadcasts

---

### Security Considerations

**Credential Management:**

- All sensitive data encrypted at rest using Fernet (symmetric encryption)
- Passwords never logged or displayed after initial generation
- SSH keys used instead of passwords where possible
- `.env` files have 600 permissions (owner read/write only)

**Network Security:**

- All communication with master server over HTTPS
- Mutual TLS for update agent authentication
- License validation uses signed tokens (JWT)
- Webhook endpoints protected by secret tokens

**Access Control:**

- Deployment wizard requires authentication
- Only authorized personnel can generate license keys
- Master server access restricted by IP whitelist
- Client instances cannot access other clients' data

**Audit Logging:**

- All deployment actions logged with timestamps
- License validation attempts tracked
- Update installations recorded
- Failed authentication attempts monitored

---

### Database Schema Extensions

New tables required in client instances to support update mechanism:

**Table: `system_updates`**

Tracks update history and status.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique update record ID |
| version | VARCHAR(20) | Version number (e.g., "1.1.0") |
| severity | VARCHAR(20) | critical, major, minor, patch |
| status | VARCHAR(20) | pending, in_progress, completed, failed, rolled_back |
| started_at | TIMESTAMP | When update began |
| completed_at | TIMESTAMP | When update finished |
| error_message | TEXT | Error details if failed |
| applied_by | VARCHAR(100) | "auto" or admin user email |

**Table: `license_validations`**

Records license check history.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PRIMARY KEY | Unique validation ID |
| validated_at | TIMESTAMP | When validation occurred |
| status | VARCHAR(20) | valid, expired, revoked, error |
| license_expires_at | TIMESTAMP | License expiration date |
| tier | VARCHAR(50) | License tier name |
| error_message | TEXT | Error if validation failed |

---

### Monitoring and Observability

**Health Check Endpoints:**

Each client instance exposes:

- `GET /health` - Basic health check (HTTP 200 if alive)
- `GET /health/detailed` - Detailed component health:
  - Database connection status
  - License validation status
  - Telegram bot connection status
  - Disk space availability
  - Service uptime

**Metrics Collection:**

The update agent can optionally report metrics to master server:

- Application uptime
- Number of active clients
- Number of active deadlines
- Database size
- Last backup timestamp
- System resource usage (CPU, RAM, disk)

**Alerting:**

Master server monitors all client instances and sends alerts for:

- License expiration approaching
- Failed update installations
- Service downtime detected
- Database backup failures
- Disk space critically low

---

## Operational Procedures

### Setting Up Master Distribution Server

**Performed by: KKT Development Team (One-Time Setup)**

**Prerequisites:**
- Access to kkt-box.net VDS
- PostgreSQL already installed and running
- Nginx already configured with SSL

**Step 1: Create Client Registry Database**

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE kkt_master_registry;

# Create user (or reuse existing)
GRANT ALL PRIVILEGES ON DATABASE kkt_master_registry TO kkt_user;

# Apply schema
\c kkt_master_registry
\i /path/to/client-registry-schema.sql
```

**Step 2: Deploy Deployment Wizard Application**

```bash
# Create directory
sudo mkdir -p /opt/kkt-deployment-wizard
cd /opt/kkt-deployment-wizard

# Clone wizard code (separate repo or branch)
git clone https://github.com/zhurbarv-hub/kkt-deployment-wizard.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env configuration
cp .env.example .env
nano .env

# Edit .env:
DATABASE_URL=postgresql://kkt_user:PASSWORD@localhost/kkt_master_registry
GITHUB_REPO=zhurbarv-hub/Qoders
GITHUB_TOKEN=ghp_your_token_here  # For API rate limits
MASTER_DOMAIN=kkt-box.net
```

**Step 3: Create Systemd Service**

```bash
# Create service file
sudo nano /etc/systemd/system/kkt-deployment-wizard.service
```

Service file content:
```ini
[Unit]
Description=KKT Deployment Wizard
After=network.target postgresql.service

[Service]
Type=simple
User=kktapp
WorkingDirectory=/opt/kkt-deployment-wizard
Environment="PATH=/opt/kkt-deployment-wizard/venv/bin"
EnvironmentFile=/opt/kkt-deployment-wizard/.env
ExecStart=/opt/kkt-deployment-wizard/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8100
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable kkt-deployment-wizard
sudo systemctl start kkt-deployment-wizard
sudo systemctl status kkt-deployment-wizard
```

**Step 4: Configure Nginx**

Add to existing Nginx configuration:

```nginx
# In /etc/nginx/sites-available/kkt-box.net

# Deployment wizard location
location /deploy/ {
    proxy_pass http://127.0.0.1:8100/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support for live deployment logs
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

```bash
# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

**Step 5: Verify Master Server Setup**

```bash
# Check wizard is accessible
curl http://localhost:8100/health

# Check via domain
curl https://kkt-box.net/deploy/health

# Verify database connection
sudo -u postgres psql -d kkt_master_registry -c "SELECT COUNT(*) FROM deployed_instances;"
```

**Estimated Time:** 30-60 minutes

---

### Deploying Real Client Instance

**Performed by: KKT Operations Team or Client (Self-Service)**

**Prerequisites:**
- Client has provisioned VDS (Ubuntu 22.04/24.04)
- Client has root/sudo SSH access
- Client has created Telegram bot via @BotFather
- Domain DNS configured (if using custom domain)

**Step 1: Gather Client Information**

Collect from client:
- VDS IP address
- SSH credentials (root password or SSH key)
- Domain name
- Telegram bot token
- Company name
- Admin details (name, email, phone)
- Admin Telegram ID(s)

**Step 2: Access Deployment Wizard**

Two options:

**Option A: Admin-Assisted Deployment**
1. Admin logs into `https://kkt-box.net/deploy`
2. Select "Production Deployment"
3. Fill in client information
4. Execute deployment

**Option B: Client Self-Service**
1. Admin generates one-time deployment token
2. Send token to client
3. Client accesses `https://kkt-box.net/deploy?token=XYZ`
4. Client fills in their own information
5. System deploys automatically

**Step 3: Monitor Deployment**

- Watch live deployment logs
- Estimated time: 30-45 minutes
- Verify each step completes successfully

**Step 4: Post-Deployment Verification**

```bash
# SSH to client VDS
ssh root@CLIENT_VDS_IP

# Check services
systemctl status kkt-web
systemctl status kkt-bot

# Check web access
curl https://CLIENT_DOMAIN/health

# Check logs
journalctl -u kkt-web -n 50
journalctl -u kkt-bot -n 50
```

**Step 5: Client Handoff**

Provide client with:
- Web interface URL
- Admin login credentials
- Telegram bot link
- Quick start guide
- Support contact information

**Step 6: Update Client Registry**

Verify instance is registered in master database:
```sql
SELECT * FROM deployed_instances WHERE domain = 'CLIENT_DOMAIN';
```

**Estimated Time:** 45-60 minutes (including handoff)

---

### Adding a New Client Instance

**Performed by: KKT Operations Team**

**Simplified Process (After MVP Tested):**

1. Client contacts sales
2. Sales provides client with deployment instructions
3. Client provisions VDS and creates bot
4. Client accesses self-service deployment wizard
5. Deployment completes automatically
6. Client receives access credentials via email
7. Operations team verifies deployment via Client Registry dashboard

**Estimated Time:** 30 minutes (mostly automated)

---

---

### Releasing a New Version

**Performed by: KKT Development Team**

**Step 1: Complete Development**

- Finish feature development
- Pass all tests in staging
- Code review approved
- Update CHANGELOG.md

**Step 2: Create Release**

```bash
# Update version
echo "1.1.0" > VERSION

# Commit changes
git add VERSION CHANGELOG.md
git commit -m "Release v1.1.0"

# Create and push tag
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main
git push origin v1.1.0
```

**Step 3: GitHub Actions Builds Release (if configured)**

Workflow automatically:
- Creates release package
- Generates checksums
- Creates GitHub Release
- Uploads assets

**Step 4: Manual Release (if GitHub Actions not used)**

```bash
# Create release package
tar -czf kkt-app-v1.1.0.tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='test_*.py' \
  --exclude='web/add_test_*.py' \
  backend/ bot/ web/ database/ deployment/ \
  requirements.txt requirements-web.txt .env.example

# Generate checksum
sha256sum kkt-app-v1.1.0.tar.gz > checksums.txt

# Create GitHub release via web UI or CLI
gh release create v1.1.0 \
  kkt-app-v1.1.0.tar.gz \
  checksums.txt \
  --title "Release v1.1.0" \
  --notes-file CHANGELOG.md
```

**Step 5: Update Client Registry**

Update master database with new version info:
```sql
INSERT INTO available_releases (version, release_date, github_url, notes)
VALUES ('1.1.0', NOW(), 'https://github.com/zhurbarv-hub/Qoders/releases/tag/v1.1.0', 'Feature updates...');
```

**Step 6: Notify Clients (Manual for MVP)**

For MVP, manually notify clients:
- Email to all registered clients
- Announcement in Telegram (if admin group exists)
- Update announcement on web dashboard

**Step 7: Test Update on Test Instance**

```bash
# SSH to kkt-box.net
ssh root@kkt-box.net

# Switch to test instance directory
cd /home/kktapp/kkt-test-system

# Check for updates
./scripts/check-updates.sh
# Output: Update available: v1.0.0 → v1.1.0

# Apply update
./scripts/apply-update.sh

# Verify update successful
cat .version  # Should show 1.1.0
systemctl status kkt-test-web kkt-test-bot
curl http://localhost:8200/health
```

**Step 8: Update Production Instance (if applicable)**

After testing on test instance:
```bash
cd /home/kktapp/kkt-system
./scripts/apply-update.sh
```

**Estimated Time:** 2-4 hours (including testing)

---

---

### Handling Failed Deployments

**Performed by: KKT Support Team**

1. Deployment failure detected via wizard or master server monitoring
2. Retrieve deployment logs from wizard backend
3. Identify failure point (system setup, database, application, services, etc.)
4. Common failure remediation:
   - SSH connection issues: Verify credentials, firewall rules
   - PostgreSQL installation failure: Check disk space, package availability
   - SSL certificate failure: Verify domain DNS, port 80 accessibility
   - Service start failure: Review application logs, check configuration
5. If auto-remediation not possible:
   - Contact client to resolve infrastructure issues
   - Provide step-by-step manual instructions
   - Offer remote assistance via screen sharing
6. After issue resolved, re-run deployment wizard from failed step
7. Document issue in knowledge base for future reference

---

### License Renewal Process

**Performed by: Client + Automated System**

1. 30 days before expiration: Automated email sent to client billing contact
2. Email includes:
   - Current license expiration date
   - Renewal instructions
   - Link to renewal payment page
3. Client completes payment via billing portal
4. Payment confirmed by billing system (Stripe webhook or manual confirmation)
5. Master server extends license expiration date
6. Client instance validates new expiration on next check (within 24 hours)
7. Confirmation email sent to client

**No Action Required by Client After Payment:** License automatically updated.

---

### Decommissioning a Client Instance

**Performed by: KKT Operations Team (with client approval)**

1. Client requests cancellation or license expires without renewal
2. Master server marks license as expired
3. Client instance detects expired license and blocks application access
4. Application displays renewal or contact support message
5. After grace period (e.g., 30 days):
   - Client receives final backup of their data (database dump)
   - Instance removed from master server registry
   - License key deactivated permanently
6. Client may choose to:
   - Keep VDS running with expired application
   - Export data and terminate VDS
   - Renew license to restore access

**Data Retention:** Client data is not deleted from their VDS - they retain full control.

---

## Billing System Variants

### Variant 1: Pay-Per-Client Subscription

**Model Description:**

Monthly subscription fee based on number of active clients tracked in the system.

**Pricing Structure:**

- Base fee: $29/month (includes up to 10 clients)
- Additional clients: $2 per client per month
- Unlimited users and cash registers

**Example Calculation:**

- Client has 45 active clients
- Base fee: $29 (covers first 10 clients)
- Additional 35 clients × $2 = $70
- Total: $99/month

**Pros:**
- Scales naturally with client business growth
- Easy to understand pricing
- Predictable costs for clients

**Cons:**
- Clients may avoid adding new clients to system to save costs
- Requires accurate client count tracking

---

### Variant 2: Flat-Rate Tiers (Recommended)

**Model Description:**

Fixed monthly fee based on usage tier as described earlier (Starter, Professional, Enterprise).

**Pricing Structure:**

| Tier | Price | Max Clients | Max Users |
|------|-------|-------------|-----------|
| Starter | $49/month | 50 | 3 |
| Professional | $99/month | 200 | 10 |
| Enterprise | $299/month | Unlimited | Unlimited |

**Pros:**
- Simple, predictable pricing
- No usage tracking complexity
- Encourages clients to use system fully

**Cons:**
- Small clients may overpay
- Large clients get significant value at Enterprise tier

---

### Variant 3: One-Time Purchase + Maintenance

**Model Description:**

One-time license purchase with optional annual maintenance subscription.

**Pricing Structure:**

- Initial license: $999 (one-time)
- Annual maintenance (optional): $199/year
  - Includes updates and bug fixes
  - Email support
  - Without maintenance: no updates after year 1

**Pros:**
- Attractive to clients who prefer one-time costs
- Higher upfront revenue
- Clear value proposition for maintenance

**Cons:**
- Cash flow less predictable
- Clients may skip maintenance and run outdated versions
- Support burden for unmaintained installations

---

### Variant 4: Freemium Model

**Model Description:**

Basic version free forever, premium features require paid upgrade.

**Pricing Structure:**

**Free Tier:**
- Up to 10 clients
- 1 user
- Telegram notifications only
- Community support

**Pro Tier ($79/month):**
- Up to 100 clients
- 5 users
- Email notifications
- API access
- Priority support

**Enterprise Tier ($249/month):**
- Unlimited everything
- Custom branding
- Dedicated support
- SLA guarantees

**Pros:**
- Low barrier to entry
- Large potential user base
- Upsell opportunities

**Cons:**
- Many users may never convert to paid
- Support costs for free users
- Feature gating adds complexity

---

## Risk Assessment and Mitigation

### Risk 1: Update Failures Cause Client Downtime

**Likelihood:** Medium  
**Impact:** High

**Mitigation Strategies:**

- Mandatory backup before every update
- Automated rollback on health check failure
- Staged rollout: apply update to 10% of instances, monitor for 24 hours, then proceed to 100%
- Maintenance window option: schedule updates during low-traffic periods
- Manual update approval for non-critical updates

---

### Risk 2: Master Server Outage Blocks Deployments

**Likelihood:** Low  
**Impact:** High (cannot deploy new instances)

**Mitigation Strategies:**

- Master server on stable VDS (kkt-box.net)
- GitHub Releases as backup (can manually download if wizard down)
- Document manual deployment process as fallback
- Monitor master server health
- Keep deployment scripts in GitHub (can run manually if needed)

---

### Risk 3: Telegram Bot API Changes Break Functionality

**Likelihood:** Medium  
**Impact:** Medium

**Mitigation Strategies:**

- Monitor Telegram Bot API changelog
- Maintain compatibility layer for API version changes
- Test bot functionality before pushing updates
- Fallback to polling if webhook fails

---

### Risk 4: Client VDS Resource Exhaustion

**Likelihood:** Medium  
**Impact:** Medium

**Mitigation Strategies:**

- Document minimum VDS requirements clearly
- Monitor disk space and alert at 80% usage
- Implement database cleanup for old notification logs
- Auto-rotate log files to prevent disk fill
- Recommend VDS upgrade path when approaching limits

---

### Risk 5: Test Deployment Affects Production

**Likelihood:** Medium  
**Impact:** Critical

**Mitigation Strategies:**

- Clear separation of test and production resources
- Different ports, databases, service names
- Wizard shows prominent warning when deploying to production VDS
- Automated check: verify production services before test deployment
- Automated check: verify production services after test deployment
- Test deployment logs clearly labeled as "TEST"

---

### Risk 6: GitHub API Rate Limits

**Likelihood:** Medium  
**Impact:** Low

**Mitigation Strategies:**

- Use authenticated GitHub API requests (higher rate limit)
- Cache release information in Client Registry
- Implement exponential backoff for API requests
- Document manual download process as fallback

---

### Risk 7: Security Vulnerability in Deployed Instances

**Likelihood:** Low  
**Impact:** Critical

**Mitigation Strategies:**

- Forced critical security updates
- Automated vulnerability scanning in CI/CD pipeline
- Security audit before each major release
- Bug bounty program for external security researchers
- Incident response plan for discovered vulnerabilities

---

## Success Metrics

### Deployment Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Deployment Success Rate | >95% | Successful deployments / total attempts |
| Average Deployment Time | <45 minutes | Time from wizard start to completion |
| Manual Intervention Required | <10% | Deployments requiring support assistance |
| First-Time Success Rate | >85% | Deployments with no retries needed |

---

### Operational Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Update Success Rate | >98% | Successful updates / total update attempts |
| Average Update Downtime | <5 minutes | Time services are offline during update |
| Rollback Rate | <2% | Updates rolled back / total updates |
| License Validation Uptime | >99.9% | Availability of license validation service |
| Instance Health | >99% | Instances passing all health checks |

---

### Business Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Client Retention Rate | >90% | Clients renewing / total clients at renewal |
| Average Revenue Per Client | $99/month | Total MRR / number of active clients |
| License Conversion Rate | >70% | Paid licenses / trial licenses |
| Support Ticket Rate | <5% | Clients submitting tickets / total clients per month |

---

## Appendices

### Appendix A: VDS Requirements

**Minimum Requirements:**

- OS: Ubuntu 22.04 LTS or 24.04 LTS
- CPU: 2 vCPUs
- RAM: 4GB
- Disk: 40GB SSD
- Network: 1Gbps connection
- Public IPv4 address

**Recommended for Production:**

- CPU: 4 vCPUs
- RAM: 8GB
- Disk: 80GB SSD
- Automated backups enabled

---

### Appendix B: Webhook Configuration Details

**Telegram Webhook Setup:**

The deployment wizard automatically configures the webhook during setup:

Request sent to Telegram API:
```
POST https://api.telegram.org/bot{TOKEN}/setWebhook
{
  "url": "https://{DOMAIN}/api/telegram/webhook",
  "secret_token": "{GENERATED_SECRET}",
  "allowed_updates": ["message", "callback_query"],
  "drop_pending_updates": true
}
```

The webhook endpoint in the application validates the secret token on every request to ensure authenticity.

---

### Appendix C: Environment Variables Reference

Complete list of environment variables configured during deployment:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| DATABASE_URL | PostgreSQL connection string | `postgresql://user:pass@localhost/dbname` | Yes |
| JWT_SECRET_KEY | Secret key for JWT tokens | Auto-generated 64-char string | Yes |
| JWT_ALGORITHM | JWT signing algorithm | `HS256` | Yes |
| JWT_EXPIRATION_HOURS | Token expiration time | `24` | Yes |
| TELEGRAM_BOT_TOKEN | Bot token from BotFather | From wizard input | Yes |
| TELEGRAM_ADMIN_IDS | Admin Telegram IDs | `123456,789012` | Yes |
| NOTIFICATION_CHECK_TIME | Daily notification time | `09:00` | Yes |
| NOTIFICATION_TIMEZONE | System timezone | `Europe/Moscow` | Yes |
| NOTIFICATION_DAYS | Alert threshold days | `14,7,3` | Yes |
| API_HOST | Web API host | `0.0.0.0` | Yes |
| API_PORT | Web API port | `8000` | Yes |
| API_RELOAD | Enable auto-reload (dev only) | `False` | Yes |
| LOG_LEVEL | Logging level | `INFO` | Yes |
| LOG_FILE | Log file path | `/var/log/kkt-system/app.log` | Yes |
| WEB_BASE_URL | Public web URL | `https://{DOMAIN}` | Yes |
| LICENSE_KEY | Client license key | From master server | Yes |
| UPDATE_AGENT_ENABLED | Enable update agent | `true` | Yes |

---

### Appendix D: Systemd Service Files

**kkt-web.service:**

```
[Unit]
Description=KKT Web Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=kktapp
WorkingDirectory=/home/kktapp/kkt-system
Environment="PATH=/home/kktapp/kkt-system/venv/bin"
EnvironmentFile=/home/kktapp/kkt-system/.env
ExecStart=/home/kktapp/kkt-system/venv/bin/uvicorn web.app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**kkt-bot.service:**

```
[Unit]
Description=KKT Telegram Bot
After=network.target kkt-web.service
Requires=kkt-web.service

[Service]
Type=simple
User=kktapp
WorkingDirectory=/home/kktapp/kkt-system
Environment="PATH=/home/kktapp/kkt-system/venv/bin"
EnvironmentFile=/home/kktapp/kkt-system/.env
ExecStart=/home/kktapp/kkt-system/venv/bin/python bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**kkt-update-agent.service:**

```
[Unit]
Description=KKT Update Agent
After=network.target

[Service]
Type=simple
User=kktapp
WorkingDirectory=/home/kktapp/kkt-system
Environment="PATH=/home/kktapp/kkt-system/venv/bin"
EnvironmentFile=/home/kktapp/kkt-system/.env
ExecStart=/home/kktapp/kkt-system/venv/bin/python update-agent/agent.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

---

### Appendix E: Backup Strategy

**Automated Backup Schedule:**

- Frequency: Daily at 03:00 (configurable)
- Retention: 7 days (older backups automatically deleted)
- Backup includes:
  - PostgreSQL database dump (compressed)
  - Application configuration files (.env)
  - Custom uploaded files (if any)

**Backup Script Location:** `/home/kktapp/backup-database.sh`

**Manual Backup:**

Admins can trigger manual backup via web interface: Settings → Database Management → Create Backup Now

**Backup Restoration:**

Restoration can be performed:
- Via web interface (upload backup file)
- Via command line (documented in deployment scripts)
- Automatically during update rollback

---

### Appendix F: Troubleshooting Common Issues

**Issue: Deployment wizard fails at SSL certificate step**

Possible causes:
- Domain DNS not pointing to VDS IP
- Port 80 blocked by firewall
- Domain already has SSL certificate from another source

Resolution:
- Verify DNS with: `dig +short {DOMAIN}`
- Check firewall: `sudo ufw status`
- Remove existing certificates: `sudo certbot delete --cert-name {DOMAIN}`
- Re-run deployment wizard from SSL step

---

**Issue: Telegram bot not receiving messages**

Possible causes:
- Webhook not properly configured
- Application not running or not accessible from internet
- Bot token invalid or revoked

Resolution:
- Check webhook status via Telegram API
- Verify web application is running: `systemctl status kkt-web`
- Test webhook URL accessibility: `curl https://{DOMAIN}/api/telegram/webhook`
- Validate bot token in `.env` file
- Restart bot service: `systemctl restart kkt-bot`

---

**Issue: Database connection errors after update**

Possible causes:
- Database migration failed
- PostgreSQL service stopped
- Connection string incorrect after update

Resolution:
- Check PostgreSQL status: `systemctl status postgresql`
- Review migration logs: `/var/log/kkt-system/migrations.log`
- Verify DATABASE_URL in `.env` file
- If migration failed, restore database backup and retry update

---

## Conclusion

This design document outlines a comprehensive, production-ready deployment system for the KKT application that supports:

- Automated, isolated deployment for multiple clients
- Interactive setup wizard with minimal technical knowledge required
- Centralized update distribution with hybrid push/pull mechanism
- Flexible billing and licensing options
- Robust rollback and error recovery mechanisms

The system is designed to scale from a few clients to hundreds while maintaining data isolation, security, and ease of management. The hybrid update distribution model balances automation with client control, ensuring critical updates are applied quickly while giving clients visibility and approval for feature updates.

Implementation of this design will enable the KKT team to efficiently onboard new clients, maintain deployed instances, and scale the business without linear increases in operational overhead.
