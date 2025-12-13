# Production Migration Plan: KKT Services Management System

## Project Overview

### System Description
KKT Services Expiration Management System is a comprehensive solution for tracking service expiration deadlines for cash registers (ККТ) with automated Telegram notifications. The system consists of three core components that must be migrated to production VDS infrastructure.

### Architecture Components

| Component | Technology | Current Port | Purpose |
|-----------|-----------|--------------|---------|
| Web Application | FastAPI + Uvicorn | 8000 | Primary web interface and REST API |
| Telegram Bot | aiogram 3.x | N/A | Automated notifications and user interactions |
| Database | SQLite 3 | N/A | Data persistence (will migrate to PostgreSQL) |

### Current Technology Stack

- **Runtime**: Python 3.6+
- **Web Framework**: FastAPI with Uvicorn ASGI server
- **Bot Framework**: aiogram 3.2.0
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT with python-jose
- **Task Scheduling**: APScheduler 3.10+
- **Current Database**: SQLite 3
- **Target Database**: PostgreSQL

## Migration Objectives

### Primary Goals

1. Deploy all three components to Linux-based VDS
2. Migrate database from SQLite to PostgreSQL
3. Configure production-grade infrastructure with Nginx reverse proxy
4. Implement SSL/TLS encryption with Let's Encrypt
5. Set up automated service management with systemd
6. Establish monitoring and backup procedures
7. Clean up unnecessary files before migration
8. Create comprehensive Git commit before deployment

### Success Criteria

- All services running stably on VDS with 99.9% uptime
- Database successfully migrated with zero data loss
- SSL certificate configured and auto-renewing
- Services auto-restart on failure or reboot
- Comprehensive logging and monitoring in place
- Backup automation configured for database
- All deprecated files removed from codebase

## Current State Analysis

### Project Structure

```
KKT/
├── web/app/              # Primary web application (FastAPI)
│   ├── api/             # API endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── static/          # Frontend assets
│   ├── config.py        # Configuration
│   └── main.py          # Application entry point
├── bot/                 # Telegram bot
│   ├── handlers/        # Command handlers
│   ├── middlewares/     # Bot middlewares
│   ├── services/        # Bot services
│   └── main.py          # Bot entry point
├── backend/             # Legacy API (assess for deprecation)
├── database/            # Database schemas and migrations
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

### Database Schema Analysis

#### Core Tables

| Table | Purpose | Key Considerations |
|-------|---------|-------------------|
| users | System administrators and support team | Contains password hashes, role-based access |
| clients | Client organizations | Contains INN validation, contact information |
| deadline_types | Service type definitions | System and custom types |
| deadlines | Service expiration tracking | Foreign keys to clients and deadline_types |
| contacts | Telegram user contacts | Links clients to Telegram IDs |
| notification_logs | Notification history | Tracks sent messages and delivery status |
| cash_registers | Cash register details | Extended functionality added in migrations |
| ofd_providers | OFD provider information | Reference data |

#### SQLite-Specific Features Requiring Attention

- **AUTOINCREMENT**: Must be converted to PostgreSQL SERIAL or IDENTITY
- **Date Functions**: `julianday()` function used in views - requires PostgreSQL equivalent
- **Boolean Type**: SQLite uses INTEGER (0/1) - PostgreSQL has native BOOLEAN
- **Text Types**: Generic TEXT type needs VARCHAR length specifications
- **Views**: Three views use SQLite date arithmetic requiring rewrite

### Environment Configuration

#### Current Local Configuration
- API Host: localhost (127.0.0.1)
- API Port: 8000
- Database: SQLite file at `database/kkt_services.db`
- CORS: Configured for localhost only
- Bot API Connection: http://localhost:8000

#### Required Production Configuration
- API Host: 0.0.0.0 (internal, behind Nginx)
- External Access: Via Nginx reverse proxy on ports 80/443
- Database: PostgreSQL connection string
- CORS: Production domain configuration
- Bot API Connection: http://localhost:8000 (internal)

## Target Infrastructure Architecture

### Server Specifications

| Component | Requirement | Justification |
|-----------|-------------|---------------|
| Operating System | Ubuntu 22.04 LTS | Long-term support, wide community adoption |
| RAM | Minimum 2GB | 1GB for applications, 0.5GB for PostgreSQL, 0.5GB for system |
| CPU | 1-2 vCPU | Sufficient for moderate load, scalable |
| Storage | 20GB SSD | Fast I/O for database operations |
| Network | 100 Mbps | Adequate for API responses and notifications |

### Production Architecture Diagram

```mermaid
flowchart TB
    subgraph Internet
        Client[Web Browser]
        TelegramAPI[Telegram API]
    end
    
    subgraph VDS["VDS Server (Ubuntu 22.04)"]
        subgraph Public["Public Layer"]
            Nginx[Nginx Reverse Proxy<br/>:80, :443<br/>SSL/TLS]
        end
        
        subgraph Application["Application Layer"]
            WebApp[Web Application<br/>FastAPI + Uvicorn<br/>:8000 internal]
            Bot[Telegram Bot<br/>aiogram<br/>Process]
        end
        
        subgraph Data["Data Layer"]
            PostgreSQL[(PostgreSQL<br/>:5432 internal)]
        end
        
        subgraph System["System Services"]
            Systemd[systemd<br/>Service Management]
            UFW[UFW Firewall]
            Certbot[Certbot<br/>SSL Automation]
        end
    end
    
    Client -->|HTTPS| Nginx
    Nginx -->|HTTP| WebApp
    WebApp --> PostgreSQL
    Bot -->|Internal API| WebApp
    Bot -->|External| TelegramAPI
    Systemd -.->|Manages| WebApp
    Systemd -.->|Manages| Bot
    UFW -.->|Protects| VDS
    Certbot -.->|Renews| Nginx
```

### Network Security Configuration

| Port | Protocol | Access | Service | Firewall Rule |
|------|----------|--------|---------|---------------|
| 22 | TCP | Restricted IP | SSH | Allow from management IP only |
| 80 | TCP | Public | HTTP (redirect to HTTPS) | Allow all |
| 443 | TCP | Public | HTTPS | Allow all |
| 8000 | TCP | Internal only | Web Application | Deny external |
| 5432 | TCP | Internal only | PostgreSQL | Deny external |

### Service Dependencies

```mermaid
graph TD
    A[PostgreSQL Service] --> B[Web Application Service]
    B --> C[Telegram Bot Service]
    B --> D[Nginx Service]
    E[Certbot Timer] --> D
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#fce4ec
```

## Migration Strategy

### Migration Phases

#### Phase 1: Pre-Migration Preparation
**Duration**: 1 day  
**Risk Level**: Low

Tasks:
- Audit codebase for deprecated files and cleanup
- Create comprehensive Git commit with all current changes
- Export current SQLite database
- Document all environment variables
- Create backup of entire project
- Test application locally with PostgreSQL connection

#### Phase 2: VDS Environment Setup
**Duration**: 4-6 hours  
**Risk Level**: Low

Tasks:
- Initial server access and security hardening
- Install system packages and dependencies
- Configure firewall rules
- Set up PostgreSQL database server
- Create application user and directories

#### Phase 3: Database Migration
**Duration**: 4-6 hours  
**Risk Level**: Medium

Tasks:
- Adapt database schema for PostgreSQL
- Create PostgreSQL database and user
- Import schema and migrate data
- Update application configuration
- Validate data integrity

#### Phase 4: Application Deployment
**Duration**: 6-8 hours  
**Risk Level**: Medium

Tasks:
- Clone repository to VDS
- Configure Python virtual environment
- Install application dependencies
- Configure environment variables
- Deploy Web Application and Bot

#### Phase 5: Infrastructure Services
**Duration**: 4-6 hours  
**Risk Level**: Low

Tasks:
- Configure Nginx reverse proxy
- Set up SSL certificates with Let's Encrypt
- Create systemd service files
- Configure service auto-restart policies

#### Phase 6: Testing and Validation
**Duration**: 4-8 hours  
**Risk Level**: Low

Tasks:
- Execute comprehensive test suite
- Verify all API endpoints
- Test Telegram bot functionality
- Validate notification system
- Performance testing under load

#### Phase 7: Production Launch
**Duration**: 2-4 hours  
**Risk Level**: High

Tasks:
- Final smoke tests
- Enable production services
- Monitor logs and metrics
- Validate external access
- Update DNS (if applicable)

### Rollback Strategy

Each phase includes rollback procedures:

| Phase | Rollback Method | Data Loss Risk |
|-------|----------------|----------------|
| Phase 1-2 | Revert to local deployment | None |
| Phase 3 | Restore SQLite database | None (backup exists) |
| Phase 4-5 | Stop services, fix configuration | None |
| Phase 6-7 | Revert to previous stable state | Minimal (log entries only) |

## Pre-Migration Preparation

### Codebase Cleanup Strategy

#### Files to Remove

| Category | Pattern | Rationale |
|----------|---------|-----------|
| Test Scripts | `test_*.py` (root level) | Development-only testing utilities |
| Batch Files | `*.bat` | Windows-specific, not needed on Linux VDS |
| Backup Files | `backups/*_README.txt` | Documentation files for local backups |
| Compilation | `build.py`, `compile.bat` | PyInstaller compilation not used in production |
| Development Logs | `logs/*.json` | Local development artifacts |
| Documentation Drafts | `*_REPORT.md`, `*_CHECKLIST.md` | Interim documentation |

#### Files to Preserve

- Core application code (`web/`, `bot/`, `backend/`)
- Database schema and migrations (`database/`)
- Configuration templates (`.env.example`)
- Production documentation (`README.md`, `INSTALL.md`)
- Requirements files (`requirements.txt`, `requirements-web.txt`)

#### Git Commit Strategy

Commit message structure:
```
Pre-production cleanup and migration preparation

- Remove development test scripts and batch files
- Clean up temporary documentation files
- Preserve core application and database schemas
- Update .gitignore for production artifacts
- Final state before VDS migration to PostgreSQL

Migration target: Ubuntu 22.04 VDS with PostgreSQL
Components: Web App + Telegram Bot + Database
```

### Data Backup Procedures

#### Local Backup Checklist

| Item | Backup Method | Location |
|------|---------------|----------|
| SQLite Database | File copy + SQL dump | Local and cloud storage |
| Environment Config | Encrypted copy of `.env` | Secure password manager |
| Static Files | Directory archive | Local backup drive |
| Git Repository | Push to remote | GitHub/GitLab |
| Migration Scripts | Include in Git | Repository |

#### Database Export Commands

Natural language description of export process:
1. Create SQL dump of entire SQLite database with schema and data
2. Export as text file with proper encoding (UTF-8)
3. Validate dump file can be read and contains all tables
4. Create JSON export of critical tables as secondary backup
5. Verify row counts match between database and export

## VDS Environment Setup

### Initial Server Configuration

#### System Requirements Installation

Package categories to install:
- **System Utilities**: build-essential, git, curl, wget, unzip
- **Python Environment**: python3.11, python3.11-venv, python3.11-dev, python3-pip
- **PostgreSQL**: postgresql, postgresql-contrib, libpq-dev
- **Web Server**: nginx
- **SSL Tools**: certbot, python3-certbot-nginx
- **Monitoring**: htop, net-tools, ufw

#### Security Hardening

| Security Measure | Configuration | Purpose |
|------------------|---------------|---------|
| SSH Key Authentication | Disable password auth | Prevent brute force attacks |
| Firewall (UFW) | Allow only 22, 80, 443 | Minimize attack surface |
| Fail2Ban | Monitor SSH attempts | Auto-block malicious IPs |
| System Updates | Configure automatic security updates | Patch vulnerabilities |
| Non-Root User | Create app-specific user | Principle of least privilege |

#### User and Directory Structure

Application user configuration:
- Username: `kktapp`
- Home directory: `/home/kktapp`
- Application directory: `/home/kktapp/kkt-system`
- Log directory: `/var/log/kkt-system`
- Service files: `/etc/systemd/system/`

Directory permissions:
- Application files: `kktapp:kktapp` with 755 for directories, 644 for files
- Log files: `kktapp:kktapp` with 755 for directory, 644 for logs
- Environment file: `kktapp:kktapp` with 600 (owner read/write only)

### PostgreSQL Installation and Configuration

#### Database Server Setup

PostgreSQL version: 14 or later (Ubuntu 22.04 default)

Initial configuration steps:
1. Install PostgreSQL server and client
2. Initialize database cluster
3. Configure PostgreSQL to listen on localhost only
4. Set strong password for postgres superuser
5. Create application database and user

#### Database and User Creation

Database specifications:
- **Database Name**: `kkt_production`
- **Owner User**: `kkt_user`
- **Encoding**: UTF8
- **Locale**: en_US.UTF-8 (or ru_RU.UTF-8)
- **Connection Limit**: 50 concurrent connections

User permissions:
- GRANT ALL PRIVILEGES on database `kkt_production`
- GRANT CONNECT on database
- GRANT CREATE on schema public
- Restrict access to only this database

#### PostgreSQL Performance Tuning

Configuration file modifications for 2GB RAM server:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| shared_buffers | 512MB | 25% of RAM for database cache |
| effective_cache_size | 1536MB | 75% of RAM for query planning |
| work_mem | 16MB | Memory for sorting operations |
| maintenance_work_mem | 128MB | Memory for VACUUM, index creation |
| max_connections | 100 | Sufficient for application needs |
| checkpoint_completion_target | 0.9 | Spread out checkpoint I/O |

### Python Environment Configuration

#### Virtual Environment Setup

Virtual environment location: `/home/kktapp/kkt-system/venv`

Setup process:
1. Create isolated Python virtual environment
2. Upgrade pip to latest version
3. Install wheel for faster package installation
4. Install production dependencies from requirements.txt
5. Verify all packages installed successfully

#### Dependency Installation

Requirements file modifications for production:
- Add `psycopg2-binary>=2.9.0` for PostgreSQL connectivity
- Add `gunicorn>=21.0.0` as alternative to uvicorn (optional)
- Remove `pyinstaller` (not needed in production)
- Pin all version numbers for reproducibility

System-level dependencies for Python packages:
- libpq-dev (for psycopg2 compilation)
- python3-dev (for building native extensions)
- gcc, g++ (for compiling C extensions)

## Database Migration Strategy

### Schema Conversion Analysis

#### SQLite to PostgreSQL Type Mapping

| SQLite Type | PostgreSQL Type | Notes |
|-------------|----------------|-------|
| INTEGER PRIMARY KEY AUTOINCREMENT | SERIAL PRIMARY KEY | or BIGSERIAL for large datasets |
| VARCHAR(n) | VARCHAR(n) | Direct mapping |
| TEXT | TEXT | Direct mapping |
| BOOLEAN | BOOLEAN | SQLite uses INTEGER 0/1 |
| TIMESTAMP | TIMESTAMP | May need timezone consideration |
| DATE | DATE | Direct mapping |

#### Auto-Increment Conversion

SQLite pattern:
```
id INTEGER PRIMARY KEY AUTOINCREMENT
```

PostgreSQL equivalent strategy:
- Use SERIAL type (creates sequence automatically)
- Alternative: IDENTITY column (SQL standard)
- Preserve existing ID values during data import
- Reset sequences to MAX(id) + 1 after import

#### Date Function Conversion

SQLite function requiring conversion:
- `julianday(date)` → PostgreSQL equivalent using date arithmetic
- `julianday(date1) - julianday(date2)` → `date1 - date2` (returns integer days)
- `CURRENT_TIMESTAMP` → Compatible in both systems

View rewrite strategy:
- Replace `julianday()` with PostgreSQL date subtraction
- Replace `CAST((julianday(date) - julianday('now')) AS INTEGER)` with `date - CURRENT_DATE`
- Test all views return identical results with sample data

### Schema Migration Process

#### Migration Script Structure

Migration approach:
1. Create base schema with tables (matching SQLite structure)
2. Create indexes for performance
3. Create views with PostgreSQL-compatible functions
4. Add constraints (foreign keys, checks)
5. Validate schema structure

#### Table Creation Order

Creation sequence (respecting foreign key dependencies):
1. users (no dependencies)
2. clients (no dependencies)
3. deadline_types (no dependencies)
4. ofd_providers (no dependencies)
5. deadlines (depends on clients, deadline_types)
6. contacts (depends on clients)
7. cash_registers (depends on clients, ofd_providers)
8. notification_logs (depends on deadlines)

#### Index Strategy

Indexes to create for optimal performance:

| Table | Index Columns | Purpose |
|-------|---------------|---------|
| users | email, is_active | Login lookup, active user filtering |
| clients | inn, name, is_active | Client search and filtering |
| deadline_types | type_name, is_active | Type lookup |
| deadlines | client_id, expiration_date, status | Core query performance |
| contacts | client_id, telegram_id | Notification routing |
| cash_registers | client_id, serial_number | Device lookup |

### Data Migration Process

#### Export from SQLite

Export strategy:
1. Generate SQL INSERT statements for all tables
2. Export data in dependency order (parent tables first)
3. Handle NULL values and special characters properly
4. Export with explicit column names (not implicit)
5. Validate export completeness

Data validation before export:
- Count total rows per table
- Identify any corrupted records
- Check for foreign key orphans
- Verify date format consistency

#### Import to PostgreSQL

Import process:
1. Disable foreign key constraints temporarily
2. Import data table by table
3. Validate row counts match export
4. Re-enable foreign key constraints
5. Update sequences to current max ID values

Sequence reset process:
- For each table with auto-increment ID
- Find MAX(id) value
- Set sequence next value to MAX(id) + 1
- Validate next insert gets correct ID

#### Data Validation

Validation checklist after migration:

| Check | Method | Expected Result |
|-------|--------|----------------|
| Row Counts | Compare SQLite and PostgreSQL table counts | Exact match |
| Sample Data | Verify random records match | Data integrity |
| Foreign Keys | Query for orphaned references | Zero orphans |
| Dates | Validate date range and formats | All dates valid |
| Boolean Values | Check 0/1 converted to true/false | Consistent conversion |
| Sequences | Test INSERT on each table | Auto-increment works |

### Configuration Updates

#### Database Connection String

Update in configuration files:

Old SQLite configuration:
```
database_url: sqlite:///database/kkt_services.db
```

New PostgreSQL configuration:
```
database_url: postgresql://kkt_user:SECURE_PASSWORD@localhost:5432/kkt_production
```

Files to update:
- `web/app/config.py` - WebSettings class
- `backend/config.py` - Settings class (if still in use)
- `.env` file - DATABASE_PATH → DATABASE_URL

#### Connection Pooling

SQLAlchemy engine configuration for production:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| pool_size | 10 | Base number of connections |
| max_overflow | 20 | Additional connections under load |
| pool_timeout | 30 | Seconds to wait for connection |
| pool_recycle | 3600 | Recycle connections every hour |
| pool_pre_ping | True | Verify connection before use |

## Application Deployment

### Repository Deployment

#### Git Clone and Configuration

Deployment location: `/home/kktapp/kkt-system`

Clone process:
1. Authenticate to Git repository (SSH key or token)
2. Clone repository to deployment directory
3. Checkout production branch (or main/master)
4. Verify all files present and correct permissions
5. Remove .git directory if not needed for updates

#### Environment Variable Configuration

Environment file location: `/home/kktapp/kkt-system/.env`

Critical environment variables for production:

| Variable | Production Value | Security Level |
|----------|-----------------|----------------|
| DATABASE_URL | PostgreSQL connection string | HIGH |
| JWT_SECRET_KEY | Strong random 64-char string | CRITICAL |
| TELEGRAM_BOT_TOKEN | From BotFather | CRITICAL |
| API_HOST | 0.0.0.0 | Low |
| API_PORT | 8000 | Low |
| API_RELOAD | False | Low |
| CORS_ORIGINS | https://yourdomain.com | Medium |
| WEB_API_BASE_URL | http://localhost:8000 | Low |
| LOG_LEVEL | INFO or WARNING | Low |

Security practices:
- Set `.env` file permissions to 600 (owner read/write only)
- Never commit `.env` to Git repository
- Store backup in encrypted password manager
- Rotate JWT secret and database password periodically

#### Static Files Configuration

Static files location: `/home/kktapp/kkt-system/web/app/static`

Nginx will serve static files directly:
- CSS: `/static/css/`
- JavaScript: `/static/js/`
- HTML: `/static/*.html`
- Images/Icons: `/static/images/` (if applicable)

File permissions: 644 (readable by all, writable by owner)

### Web Application Deployment

#### Application Structure

Main application file: `/home/kktapp/kkt-system/web/app/main.py`

Service will run via uvicorn ASGI server:
- Worker class: Uvicorn worker
- Workers: 2 (for 2GB RAM server)
- Bind address: 127.0.0.1:8000 (localhost only)
- Timeout: 60 seconds
- Keepalive: 5 seconds

#### Startup Validation

Pre-launch checklist:
1. Database connection successful
2. All environment variables loaded
3. Static files directory accessible
4. API routes registered correctly
5. CORS configuration appropriate
6. JWT secret key loaded

Health check endpoint:
- URL: `/health`
- Response: JSON with status, database connectivity
- Used by: Nginx for upstream health, monitoring tools

### Telegram Bot Deployment

#### Bot Configuration

Main bot file: `/home/kktapp/kkt-system/bot/main.py`

Bot configuration requirements:
- Telegram bot token from environment
- Admin Telegram IDs configured
- Web API connection to localhost:8000
- Scheduler configured for notification times
- Timezone set correctly (Europe/Moscow or as needed)

#### Bot Service Dependencies

Bot depends on Web Application:
- Must start AFTER web application is running
- Uses Web API client for data access
- Requires valid JWT token from Web API
- Falls back gracefully if Web API unavailable

Service dependency configuration:
- Requires: kkt-web.service
- After: kkt-web.service postgresql.service
- Restart policy: Always restart on failure

#### Notification Schedule

Scheduler configuration:
- Daily check time: As configured in NOTIFICATION_CHECK_TIME
- Timezone: As configured in NOTIFICATION_TIMEZONE
- Notification days: 14, 7, 3 days before expiration
- Retry policy: 3 attempts with 5-minute delays

Logging strategy:
- Log all notification attempts
- Record success/failure status
- Track Telegram API errors
- Daily summary to administrators

## Infrastructure Services Configuration

### Nginx Reverse Proxy

#### Nginx Configuration Structure

Configuration file: `/etc/nginx/sites-available/kkt-system`
Symlink: `/etc/nginx/sites-enabled/kkt-system`

Configuration sections:
1. Upstream definition (backend application)
2. HTTP server block (redirect to HTTPS)
3. HTTPS server block (main configuration)
4. Static file serving
5. API proxy configuration
6. Security headers

#### Upstream Configuration

Upstream backend definition:
- Name: `kkt_backend`
- Server: `127.0.0.1:8000`
- Backup: None (single application server)
- Health check: Passive (monitor failures)
- Keepalive connections: 32

Load balancing: Not applicable (single server)
Failover: Application-level restart via systemd

#### Server Block Configuration

HTTP Server (Port 80):
- Purpose: Redirect all HTTP to HTTPS
- Listen: 0.0.0.0:80
- Server name: Your domain name
- Return: 301 redirect to https://

HTTPS Server (Port 443):
- Listen: 0.0.0.0:443 ssl http2
- SSL certificate: Let's Encrypt
- SSL protocols: TLSv1.2, TLSv1.3
- SSL ciphers: Strong ciphers only
- HSTS: Enabled with 1-year max-age

#### Location Blocks

| Location | Purpose | Configuration |
|----------|---------|---------------|
| `/static/` | Serve static files | Direct file serving from disk |
| `/api/` | Proxy API requests | Proxy to upstream with headers |
| `/` | Redirect to login | Redirect to /static/login.html |
| `/health` | Health check | Proxy to upstream, used for monitoring |

#### Proxy Headers

Headers to pass to backend:

| Header | Value | Purpose |
|--------|-------|---------|
| Host | $host | Preserve original host |
| X-Real-IP | $remote_addr | Client real IP address |
| X-Forwarded-For | $proxy_add_x_forwarded_for | Proxy chain |
| X-Forwarded-Proto | $scheme | Original protocol (https) |
| X-Forwarded-Host | $host | Original host header |

#### Security Headers

Headers to add in response:

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | nosniff | Prevent MIME sniffing |
| X-Frame-Options | DENY | Prevent clickjacking |
| X-XSS-Protection | 1; mode=block | XSS protection |
| Strict-Transport-Security | max-age=31536000 | Force HTTPS |
| Content-Security-Policy | Restrictive policy | Prevent XSS attacks |

### SSL/TLS Configuration

#### Let's Encrypt Certificate

Certbot installation and usage:
1. Install certbot with nginx plugin
2. Run certbot with nginx plugin for automatic configuration
3. Provide domain name and email for renewal notices
4. Allow certbot to modify nginx configuration
5. Verify certificate installation successful

Certificate details:
- Provider: Let's Encrypt
- Validity: 90 days
- Renewal: Automatic via certbot timer
- Location: `/etc/letsencrypt/live/yourdomain.com/`

#### Auto-Renewal Configuration

Certbot timer service:
- Service: `certbot.timer`
- Schedule: Twice daily
- Renewal threshold: 30 days before expiration
- Post-renewal hook: Reload nginx

Manual renewal test command available for validation.

#### SSL Security Best Practices

SSL configuration parameters:

| Parameter | Value | Security Benefit |
|-----------|-------|------------------|
| ssl_protocols | TLSv1.2 TLSv1.3 | Modern protocols only |
| ssl_prefer_server_ciphers | on | Server chooses cipher |
| ssl_ciphers | HIGH:!aNULL:!MD5 | Strong ciphers only |
| ssl_session_cache | shared:SSL:10m | Performance + security |
| ssl_session_timeout | 10m | Limit session reuse window |
| ssl_stapling | on | OCSP stapling for performance |

### Systemd Service Configuration

#### Web Application Service

Service file: `/etc/systemd/system/kkt-web.service`

Service configuration:

| Directive | Value | Purpose |
|-----------|-------|---------|
| Type | notify | Systemd-aware service |
| User | kktapp | Run as non-root user |
| WorkingDirectory | /home/kktapp/kkt-system | Application root |
| ExecStart | Uvicorn command | Start web application |
| Restart | always | Auto-restart on failure |
| RestartSec | 10 | Wait before restart |

Environment:
- Load from `/home/kktapp/kkt-system/.env`
- Override specific variables if needed

Dependencies:
- After: network.target postgresql.service
- Wants: postgresql.service

#### Telegram Bot Service

Service file: `/etc/systemd/system/kkt-bot.service`

Service configuration:

| Directive | Value | Purpose |
|-----------|-------|---------|
| Type | simple | Standard daemon process |
| User | kktapp | Run as non-root user |
| WorkingDirectory | /home/kktapp/kkt-system | Application root |
| ExecStart | Python bot main | Start Telegram bot |
| Restart | always | Auto-restart on failure |
| RestartSec | 10 | Wait before restart |

Dependencies:
- After: network.target kkt-web.service
- Requires: kkt-web.service
- BindsTo: kkt-web.service (stop if web app stops)

#### Service Management Commands

Service control operations:
- Enable services for auto-start on boot
- Start services immediately
- Check status and logs
- Reload systemd daemon after config changes
- View real-time logs with journalctl

Service dependency graph:
```mermaid
graph TD
    A[System Boot] --> B[network.target]
    A --> C[postgresql.service]
    B --> D[kkt-web.service]
    C --> D
    D --> E[kkt-bot.service]
    D --> F[nginx.service]
    
    style A fill:#e3f2fd
    style C fill:#f3e5f5
    style D fill:#fff3e0
    style E fill:#e8f5e9
    style F fill:#fce4ec
```

## Security Configuration

### Firewall Rules (UFW)

#### Default Policies

Firewall default behavior:
- Default incoming: DENY
- Default outgoing: ALLOW
- Default routed: DENY

Rationale: Minimize attack surface by blocking all incoming except explicitly allowed.

#### Allowed Services

| Port/Service | Protocol | Source | Purpose |
|--------------|----------|--------|---------|
| 22/SSH | TCP | Specific IP (optional) | Remote administration |
| 80/HTTP | TCP | Any | Web access (redirects to HTTPS) |
| 443/HTTPS | TCP | Any | Secure web access |

Advanced SSH protection:
- Optionally limit SSH to specific management IPs
- Use non-standard SSH port (security through obscurity)
- Implement rate limiting with UFW

#### Rate Limiting

Rate limit configuration for SSH:
- Limit connections to 6 attempts per 30 seconds
- Automatically blocks brute force attempts
- Temporary blocks (configurable duration)

### Secrets Management

#### Environment Variable Security

Security measures for `.env` file:
- File permissions: 600 (owner read/write only)
- Owner: kktapp user
- Never commit to version control
- Backup encrypted in secure location

#### JWT Secret Key

Requirements:
- Minimum length: 64 characters
- Character set: Alphanumeric + special characters
- Randomness: Cryptographically secure random generation
- Rotation: Plan for periodic rotation

Generation method: Use system-provided secure random generator.

#### Database Credentials

PostgreSQL password requirements:
- Length: Minimum 16 characters
- Complexity: Mix of upper, lower, digits, special chars
- Uniqueness: Not used for any other service
- Storage: Only in `.env` file and password manager

Connection security:
- PostgreSQL accepts only localhost connections
- No remote database access allowed
- SSL not required for localhost connections

#### Telegram Bot Token

Token security:
- Obtain from @BotFather in Telegram
- Store only in environment variable
- Never log or expose in error messages
- Regenerate if compromised

### Backup Strategy

#### Database Backup Configuration

Backup schedule:
- Frequency: Daily at 3:00 AM local time
- Retention: Keep last 7 daily backups
- Method: PostgreSQL pg_dump
- Format: Custom compressed format

Backup storage:
- Local: `/home/kktapp/backups/database/`
- Remote: Cloud storage (S3, BackBlaze, etc.) - recommended
- Permissions: 600 (owner read/write only)

Backup validation:
- Test restore monthly
- Verify backup file integrity
- Check backup file size (detect corruption)
- Alert on backup failure

#### Application Backup

Files to backup:
- Environment configuration (`.env`) - encrypted
- Static files (if user-uploaded content exists)
- Log files (optional, for forensics)
- Nginx configuration
- Systemd service files

Backup frequency: Weekly or on configuration changes

#### Backup Automation

Backup script approach:
- Create shell script for pg_dump with rotation
- Create systemd timer for scheduled execution
- Log backup results
- Send notification on failure

Restore procedure documentation:
- Document step-by-step restore process
- Test restore in staging environment
- Include recovery time objective (RTO)

## Testing and Validation Strategy

### Pre-Deployment Testing

#### Local PostgreSQL Testing

Test environment setup:
1. Install PostgreSQL locally on development machine
2. Import production-ready schema
3. Run application with PostgreSQL connection
4. Execute all test suites
5. Verify functionality matches SQLite behavior

Test coverage areas:
- Database connection and pooling
- CRUD operations on all tables
- Foreign key constraint enforcement
- Date calculations and view queries
- Transaction handling

#### Configuration Validation

Configuration tests:
- Verify all environment variables load correctly
- Test database connection string
- Validate JWT token generation and verification
- Check CORS origins configuration
- Confirm Telegram bot token validity

### Deployment Testing

#### Smoke Tests

Immediate post-deployment checks:

| Test | Method | Expected Result |
|------|--------|-----------------|
| Web app running | Check systemd status | Active (running) |
| Bot running | Check systemd status | Active (running) |
| Database connected | Query health endpoint | Status: healthy |
| Nginx responding | HTTP request to domain | 301 redirect to HTTPS |
| HTTPS working | HTTPS request | Valid certificate, 200 OK |

#### Functional Testing

API endpoint testing:

| Endpoint | Test Case | Expected Response |
|----------|-----------|-------------------|
| POST /api/auth/login | Valid credentials | JWT token returned |
| GET /api/clients | Authenticated request | List of clients |
| GET /api/deadlines | Filter by expiring soon | Filtered results |
| GET /api/dashboard/stats | Request statistics | Dashboard data |
| POST /api/deadlines | Create new deadline | 201 Created |

Frontend testing:
- Login page loads correctly
- Authentication flow works
- Dashboard displays data
- Client management operations
- Deadline creation and editing

#### Telegram Bot Testing

Bot functionality tests:

| Command | Test Scenario | Expected Behavior |
|---------|--------------|-------------------|
| /start | New user registration | Welcome message, registration flow |
| /list | List deadlines | Display client's deadlines |
| /today | Today's deadlines | Show deadlines expiring today |
| /search | Search by client name | Return matching results |
| /export | Request data export | Generate and send export file |

Notification testing:
- Trigger manual notification
- Verify delivery to Telegram
- Check notification log in database
- Validate message formatting

### Performance Testing

#### Load Testing

Load test scenarios:

| Scenario | Concurrent Users | Duration | Target Metric |
|----------|-----------------|----------|---------------|
| Normal load | 10 | 10 minutes | < 200ms avg response |
| Peak load | 50 | 5 minutes | < 500ms avg response |
| Stress test | 100 | 2 minutes | No crashes, graceful degradation |

Metrics to monitor:
- Average response time
- 95th percentile response time
- Error rate (target: < 0.1%)
- CPU usage (target: < 70%)
- Memory usage (target: < 80%)

#### Database Performance

Query performance benchmarks:
- Dashboard statistics query: < 100ms
- Client list with pagination: < 50ms
- Deadline search query: < 100ms
- Complex joins in views: < 200ms

Index effectiveness:
- Verify indexes used in query plans
- Check for sequential scans on large tables
- Optimize slow queries identified

### Security Testing

#### SSL/TLS Validation

SSL tests:
- Certificate validity and chain of trust
- Protocol versions (only TLSv1.2, TLSv1.3 allowed)
- Cipher suite strength
- HSTS header present
- Certificate expiration date

External validation tools:
- SSL Labs test (target: A+ rating)
- Security headers check
- Certificate transparency logs

#### Access Control Testing

Authentication tests:
- Unauthenticated requests rejected
- Invalid tokens rejected
- Expired tokens rejected
- Role-based access control works
- SQL injection prevention

Authorization tests:
- Users can only access own data
- Admins can access all data
- Cross-client data access blocked

#### Firewall Validation

Network security tests:
- Port 22: Accessible (from allowed IPs)
- Port 80: Accessible, redirects to HTTPS
- Port 443: Accessible, valid SSL
- Port 8000: NOT accessible externally
- Port 5432: NOT accessible externally

### Monitoring Setup

#### Application Logging

Log configuration:

| Log Type | Location | Rotation | Retention |
|----------|----------|----------|-----------|
| Web app logs | /var/log/kkt-system/web.log | Daily | 30 days |
| Bot logs | /var/log/kkt-system/bot.log | Daily | 30 days |
| Nginx access | /var/log/nginx/access.log | Daily | 14 days |
| Nginx error | /var/log/nginx/error.log | Daily | 30 days |
| PostgreSQL | /var/log/postgresql/ | Weekly | 30 days |

Log levels:
- Production: INFO or WARNING
- Include timestamps with timezone
- Structured logging (JSON) for parsing
- Exclude sensitive data (passwords, tokens)

#### Health Monitoring

Monitoring strategy:
- Internal: Application health endpoint
- External: Uptime monitoring service (optional)
- Database: Connection pool status
- System: CPU, memory, disk usage

Alerting thresholds:

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU usage | 70% | 90% |
| Memory usage | 80% | 95% |
| Disk usage | 75% | 90% |
| Response time | 500ms | 1000ms |
| Error rate | 1% | 5% |

#### Metrics Collection

Key metrics to track:
- Request count per endpoint
- Average response time
- Active database connections
- Telegram bot message count
- Notification delivery rate
- Daily active users

Optional: Integrate with monitoring platforms (Prometheus, Grafana, etc.)

## Rollback Strategy

### Rollback Triggers

Conditions requiring rollback:

| Condition | Severity | Action |
|-----------|----------|--------|
| Database corruption | Critical | Immediate rollback |
| Authentication failure | Critical | Immediate rollback |
| Data loss detected | Critical | Immediate rollback |
| Performance degradation > 300% | High | Rollback within 1 hour |
| Non-critical feature broken | Medium | Fix forward or rollback |

### Rollback Procedures

#### Phase-Specific Rollback

**If rollback during Database Migration (Phase 3):**
1. Stop all application services
2. Drop PostgreSQL database
3. Restore SQLite database from backup
4. Revert configuration to SQLite connection
5. Restart services with SQLite
6. Validate data integrity

**If rollback during Application Deployment (Phase 4-5):**
1. Stop systemd services
2. Restore previous Git commit
3. Restore previous .env configuration
4. Restart services
5. Verify functionality restored

**If rollback after Production Launch (Phase 7):**
1. Enable maintenance mode (Nginx redirect)
2. Stop current services
3. Restore database from last known good backup
4. Restore application code to previous version
5. Restart services
6. Validate all functionality
7. Disable maintenance mode

### Data Recovery

#### Point-in-Time Recovery

Recovery strategy:
- Use daily PostgreSQL backups
- Maximum data loss: 24 hours (last backup)
- Recovery time objective: 2 hours
- Recovery point objective: Last midnight backup

Recovery steps:
1. Identify backup timestamp to restore
2. Stop application services
3. Drop current database
4. Restore from backup file
5. Verify data integrity
6. Restart services

#### Transaction Log Recovery

PostgreSQL WAL (Write-Ahead Logging):
- Enable WAL archiving for point-in-time recovery (optional)
- Allows recovery to specific transaction
- Requires additional disk space
- More complex configuration

Recommended for: High-value production systems with zero data loss tolerance

## Post-Migration Tasks

### Monitoring and Optimization

#### Initial Observation Period

Post-launch monitoring duration: 7 days intensive monitoring

Daily checks:
- Review application logs for errors
- Check database performance metrics
- Monitor system resource usage
- Verify backup completion
- Review Telegram notification delivery

#### Performance Optimization

Optimization opportunities:

| Area | Metric | Optimization |
|------|--------|--------------|
| Database | Slow queries > 100ms | Add indexes, optimize queries |
| API | Response time > 200ms | Enable caching, optimize code |
| Static files | Load time > 1s | Enable Nginx gzip compression |
| Bot | Message delay > 2s | Review API call efficiency |

Database maintenance:
- Run VACUUM ANALYZE weekly
- Monitor table bloat
- Review and optimize slow queries
- Consider read replicas if needed (future)

### Documentation Updates

#### Operational Documentation

Documents to create/update:

| Document | Content | Audience |
|----------|---------|----------|
| Deployment Guide | Step-by-step deployment process | DevOps team |
| Operations Runbook | Common tasks and troubleshooting | Support team |
| Disaster Recovery Plan | Backup and restore procedures | All technical staff |
| Security Audit Log | Changes to security configuration | Security team |
| API Documentation | Updated endpoints and examples | Developers, integrators |

#### Knowledge Transfer

Knowledge areas to document:
- VDS access credentials and procedures
- Database backup and restore process
- Service restart and debugging
- Log file locations and analysis
- Common issues and resolutions

### User Communication

#### Stakeholder Notification

Communication plan:

| Stakeholder | Timing | Channel | Content |
|-------------|--------|---------|---------|
| End users | 48h before | Email, Telegram | Migration schedule, expected downtime |
| Administrators | 1 week before | Email | Technical details, testing required |
| Management | 1 week before | Email | Timeline, risks, rollback plan |
| All users | After migration | Email, Telegram | Confirmation, new URLs if applicable |

#### Migration Announcement

Announcement should include:
- Migration date and time
- Expected downtime window
- What changes users will see (if any)
- New URLs or access methods (if changed)
- Contact for issues or questions

### Maintenance Schedule

#### Regular Maintenance Tasks

| Task | Frequency | Owner | Purpose |
|------|-----------|-------|---------|
| Database backup verification | Weekly | DevOps | Ensure recoverability |
| Log review | Daily (first week), then weekly | Support | Identify issues early |
| Security updates | Weekly | DevOps | Patch vulnerabilities |
| SSL certificate check | Monthly | DevOps | Prevent expiration |
| Performance review | Monthly | DevOps | Identify optimization needs |
| Disk space monitoring | Weekly | DevOps | Prevent out-of-space errors |

#### Update Procedures

Application update process:
1. Test updates in local/staging environment
2. Create database backup
3. Schedule maintenance window
4. Deploy updates via Git pull
5. Restart services
6. Verify functionality
7. Monitor for issues

Database schema updates:
1. Create migration script
2. Test on backup database copy
3. Schedule maintenance window
4. Backup production database
5. Apply migration
6. Verify data integrity
7. Update application code if needed

## Deployment Checklist

### Pre-Migration Checklist

#### Preparation Phase

- [ ] Codebase cleanup completed (test files, batch files removed)
- [ ] Git repository committed with descriptive message
- [ ] Git repository pushed to remote (GitHub/GitLab)
- [ ] SQLite database exported and backed up locally
- [ ] SQLite database exported and backed up to cloud storage
- [ ] Current .env file backed up securely
- [ ] All environment variables documented
- [ ] Local PostgreSQL testing completed successfully
- [ ] All dependencies verified in requirements.txt
- [ ] VDS account created and accessible
- [ ] Domain name registered and DNS configured (if applicable)
- [ ] SSH key authentication configured for VDS access

### VDS Setup Checklist

#### Server Configuration

- [ ] Initial server access verified via SSH
- [ ] Root password changed to strong password
- [ ] Non-root user (kktapp) created
- [ ] SSH key authentication configured for kktapp user
- [ ] System packages updated to latest versions
- [ ] UFW firewall installed and configured
- [ ] Fail2Ban installed and configured
- [ ] Python 3.11+ installed
- [ ] PostgreSQL installed and running
- [ ] Nginx installed
- [ ] Certbot installed
- [ ] Git installed
- [ ] Required system libraries installed (libpq-dev, etc.)

### Database Setup Checklist

#### PostgreSQL Configuration

- [ ] PostgreSQL service running and enabled
- [ ] Database 'kkt_production' created
- [ ] Database user 'kkt_user' created with strong password
- [ ] User permissions granted on database
- [ ] PostgreSQL configured to listen on localhost only
- [ ] Schema imported successfully
- [ ] Data migrated from SQLite
- [ ] Row counts verified (SQLite vs PostgreSQL)
- [ ] Foreign key constraints validated
- [ ] Sequences reset to correct values
- [ ] Views tested and returning correct results
- [ ] Sample queries executed successfully
- [ ] Database backup tested and verified

### Application Deployment Checklist

#### Code Deployment

- [ ] Repository cloned to /home/kktapp/kkt-system
- [ ] Correct branch checked out (main/master/production)
- [ ] File permissions set correctly (kktapp:kktapp)
- [ ] Virtual environment created
- [ ] Dependencies installed from requirements.txt
- [ ] psycopg2-binary installed for PostgreSQL
- [ ] .env file created with production values
- [ ] .env file permissions set to 600
- [ ] Database connection tested successfully
- [ ] Static files directory verified
- [ ] Log directory created (/var/log/kkt-system)
- [ ] Application starts manually without errors

### Service Configuration Checklist

#### Systemd Services

- [ ] kkt-web.service file created
- [ ] kkt-bot.service file created
- [ ] Service files have correct paths and commands
- [ ] Service dependencies configured correctly
- [ ] Systemd daemon reloaded
- [ ] Services enabled for auto-start
- [ ] Services started successfully
- [ ] Service status verified (active/running)
- [ ] Service logs checked for errors
- [ ] Services restart automatically on failure (tested)

### Web Server Configuration Checklist

#### Nginx Setup

- [ ] Nginx configuration file created
- [ ] Upstream backend configured
- [ ] Server blocks configured (HTTP and HTTPS)
- [ ] Static file serving configured
- [ ] API proxy configuration completed
- [ ] Proxy headers configured
- [ ] Security headers configured
- [ ] Configuration syntax tested (nginx -t)
- [ ] Nginx service restarted
- [ ] HTTP to HTTPS redirect working
- [ ] Static files accessible via Nginx

#### SSL Configuration

- [ ] Let's Encrypt certificate requested
- [ ] Certificate installed successfully
- [ ] Certificate chain validated
- [ ] Auto-renewal configured
- [ ] Certbot timer enabled
- [ ] HTTPS working with valid certificate
- [ ] SSL Labs test passed (A+ rating)
- [ ] HSTS header present

### Security Checklist

#### Firewall and Access Control

- [ ] UFW firewall enabled
- [ ] Port 22 allowed (SSH)
- [ ] Port 80 allowed (HTTP)
- [ ] Port 443 allowed (HTTPS)
- [ ] Port 8000 blocked externally
- [ ] Port 5432 blocked externally
- [ ] SSH rate limiting configured
- [ ] Password authentication disabled for SSH
- [ ] Root login disabled via SSH

#### Secrets and Credentials

- [ ] JWT secret key is strong and unique
- [ ] Database password is strong and unique
- [ ] Telegram bot token configured correctly
- [ ] SMTP credentials configured (if using email)
- [ ] All secrets stored only in .env file
- [ ] .env file permissions verified (600)
- [ ] Backup of .env stored securely encrypted

### Testing Checklist

#### Functional Testing

- [ ] Web application accessible via domain/IP
- [ ] HTTPS working without browser warnings
- [ ] Login functionality working
- [ ] Dashboard displays correctly
- [ ] Client management CRUD operations working
- [ ] Deadline management CRUD operations working
- [ ] API endpoints responding correctly
- [ ] Telegram bot responding to commands
- [ ] Bot /start command working
- [ ] Bot /list command showing correct data
- [ ] Bot /search functionality working
- [ ] Notification scheduler running
- [ ] Test notification sent successfully
- [ ] Notification logged in database

#### Performance Testing

- [ ] Average response time < 200ms
- [ ] Database queries performing adequately
- [ ] No memory leaks observed
- [ ] CPU usage within acceptable limits
- [ ] No slow query warnings in logs

### Backup and Recovery Checklist

#### Backup Configuration

- [ ] Database backup script created
- [ ] Backup cron job or timer configured
- [ ] Backup retention policy configured
- [ ] Backup storage location verified
- [ ] First backup completed successfully
- [ ] Backup restore tested successfully
- [ ] Remote backup configured (optional)

### Monitoring Checklist

#### Logging and Monitoring

- [ ] Application logs configured
- [ ] Log rotation configured
- [ ] Nginx logs accessible
- [ ] PostgreSQL logs accessible
- [ ] Health check endpoint working
- [ ] System resource monitoring in place
- [ ] Alert thresholds defined
- [ ] Log review schedule established

### Final Verification Checklist

#### Go-Live Verification

- [ ] All services running and stable
- [ ] No critical errors in logs
- [ ] Database connectivity verified
- [ ] External HTTPS access working
- [ ] Telegram bot responding
- [ ] Notifications being sent
- [ ] Backup completed successfully
- [ ] Rollback plan documented and ready
- [ ] Support team briefed
- [ ] Users notified of migration completion
- [ ] DNS updated to production server (if applicable)
- [ ] Monitoring dashboards configured
- [ ] Incident response plan documented

### Post-Migration Checklist

#### Follow-Up Tasks

- [ ] Monitor logs daily for first week
- [ ] Verify backups completing daily
- [ ] Review performance metrics
- [ ] Collect user feedback
- [ ] Address any reported issues
- [ ] Update documentation based on lessons learned
- [ ] Schedule follow-up optimization review
- [ ] Plan for next maintenance window

## Migration Timeline

### Estimated Timeline by Phase

| Phase | Duration | Complexity | Risk Level |
|-------|----------|------------|------------|
| Pre-Migration Preparation | 1 day | Medium | Low |
| VDS Environment Setup | 4-6 hours | Medium | Low |
| Database Migration | 4-6 hours | High | Medium |
| Application Deployment | 6-8 hours | Medium | Medium |
| Infrastructure Services | 4-6 hours | Medium | Low |
| Testing & Validation | 4-8 hours | Low | Low |
| Production Launch | 2-4 hours | Low | High |
| **Total Estimated Time** | **2-3 days** | - | - |

### Recommended Schedule

**Day 1: Preparation and Setup**
- Morning: Pre-migration preparation and cleanup
- Afternoon: VDS environment setup
- Evening: Database migration preparation

**Day 2: Migration and Deployment**
- Morning: Database migration to PostgreSQL
- Afternoon: Application deployment
- Evening: Infrastructure services configuration

**Day 3: Testing and Launch**
- Morning: Comprehensive testing
- Afternoon: Final validation and production launch
- Evening: Monitoring and initial observation

### Maintenance Windows

Recommended migration timing:
- **Best time**: Weekend or off-peak hours
- **Expected downtime**: 2-4 hours during database migration
- **Notification lead time**: 48 hours minimum to all users

## Risk Assessment and Mitigation

### High-Risk Areas

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| Data loss during migration | Low | Critical | Multiple backups, validation checkpoints |
| Database corruption | Low | Critical | PostgreSQL ACID compliance, transaction safety |
| Extended downtime | Medium | High | Thorough testing, rollback plan ready |
| Configuration errors | Medium | Medium | Checklists, peer review, staged deployment |
| SSL certificate issues | Low | Medium | Test certbot in advance, manual fallback |
| Service dependencies failure | Medium | Medium | Proper systemd dependency configuration |

### Mitigation Strategies

**Data Protection:**
- Maintain SQLite backup until PostgreSQL proven stable (1 week minimum)
- Daily PostgreSQL backups with verification
- Transaction-based data migration with rollback capability
- Row count validation at each migration step

**Availability:**
- Rollback plan tested and ready
- Service health monitoring with automatic alerts
- Systemd auto-restart configuration
- Nginx upstream health checks

**Security:**
- Security hardening before going live
- Firewall rules tested before enabling
- Regular security updates schedule
- Principle of least privilege for all services

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Uptime | > 99.5% | Monitoring service or health checks |
| Average response time | < 200ms | Application logging, load testing |
| Database query time | < 100ms (95th percentile) | PostgreSQL slow query log |
| Error rate | < 0.1% | Application error logs |
| Notification delivery | > 99% | Notification logs analysis |

### Business Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| User satisfaction | > 90% positive | User feedback survey |
| Support tickets | < 5 per week | Ticket tracking system |
| Data accuracy | 100% | Manual audit vs source data |
| Service availability | 24/7 | Uptime monitoring |

### Post-Migration Success Indicators

Week 1 indicators:
- No critical errors in logs
- All scheduled notifications sent successfully
- User login success rate > 95%
- Database backups completing without errors
- No rollback required

Month 1 indicators:
- Performance metrics within targets
- No data integrity issues discovered
- SSL certificate auto-renewal working
- Backup and restore tested successfully
- Optimization opportunities identified and planned

## Appendices

### Technology Reference

#### Key Technologies

| Technology | Version | Documentation URL |
|------------|---------|-------------------|
| Ubuntu Server | 22.04 LTS | https://ubuntu.com/server/docs |
| Python | 3.11+ | https://docs.python.org/3/ |
| FastAPI | 0.104+ | https://fastapi.tiangolo.com/ |
| PostgreSQL | 14+ | https://www.postgresql.org/docs/ |
| Nginx | 1.18+ | https://nginx.org/en/docs/ |
| aiogram | 3.2+ | https://docs.aiogram.dev/ |
| SQLAlchemy | 2.0+ | https://docs.sqlalchemy.org/ |

### Command Reference

Critical commands for operations:

**Service Management:**
- Check service status
- Start/stop/restart services
- View service logs
- Enable/disable auto-start

**Database Operations:**
- PostgreSQL backup creation
- Database restore
- Connection testing
- Query performance analysis

**Nginx Operations:**
- Test configuration syntax
- Reload configuration
- View access/error logs
- Certificate renewal

**System Operations:**
- Firewall rule management
- User permission management
- Disk space monitoring
- Process monitoring

### Contact Information

#### Escalation Path

| Issue Severity | Contact | Response Time |
|----------------|---------|---------------|
| Critical (System down) | DevOps Lead | Immediate |
| High (Service degraded) | DevOps Team | < 1 hour |
| Medium (Non-critical bug) | Development Team | < 4 hours |
| Low (Feature request) | Product Manager | < 1 business day |

#### Support Resources

- **Documentation**: Project repository README.md
- **Issue Tracking**: GitHub Issues or internal ticketing system
- **Communication**: Slack/Teams channel for technical team
- **Monitoring**: Dashboard URL (if configured)

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-13  
**Prepared For**: KKT System Production Migration  
**Target Platform**: Linux VDS (Ubuntu 22.04) with PostgreSQL  
**Migration Type**: Full stack (Frontend + Backend + Bot + Database)
