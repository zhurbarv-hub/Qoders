# KKT System Deployment Design Document

## Document Overview

**Purpose**: Define the strategic design and deployment architecture for the KKT (Cash Register Control) system migration from local SQLite environment to production VDS infrastructure with PostgreSQL.

**Scope**: Complete production deployment workflow including infrastructure setup, database migration, application deployment, service configuration, and operational monitoring.

**Target Environment**: Ubuntu 22.04 LTS VDS with PostgreSQL 14+, Nginx, and systemd service management.

---

## System Architecture Overview

### High-Level Architecture

The KKT system consists of three primary components deployed on a single VDS instance:

```mermaid
graph TB
    subgraph "External Layer"
        Users[Web Users]
        TG[Telegram Users]
        Domain[Domain Name + SSL]
    end
    
    subgraph "VDS Server - Ubuntu 22.04"
        subgraph "Reverse Proxy Layer"
            Nginx[Nginx + Let's Encrypt SSL]
        end
        
        subgraph "Application Layer"
            WebApp[FastAPI Web Application<br/>Port 8000]
            Bot[Telegram Bot<br/>aiogram 3.x]
        end
        
        subgraph "Data Layer"
            PG[(PostgreSQL 14+<br/>kkt_production)]
            Backups[Automated Daily Backups]
        end
        
        subgraph "System Services"
            Systemd[systemd Service Manager]
            UFW[UFW Firewall]
        end
    end
    
    Users -->|HTTPS:443| Domain
    TG -->|Telegram API| Bot
    Domain --> Nginx
    Nginx -->|Reverse Proxy| WebApp
    Bot -->|HTTP API| WebApp
    WebApp --> PG
    Systemd -->|Manages| WebApp
    Systemd -->|Manages| Bot
    PG -->|pg_dump| Backups
    UFW -->|Protects| Nginx
```

### Component Responsibilities

| Component | Responsibility | Technology Stack |
|-----------|---------------|------------------|
| Web Application | REST API, authentication, business logic, admin dashboard | FastAPI, Uvicorn, JWT |
| Telegram Bot | User interface, notifications, conversational interactions | aiogram 3.x, asyncio |
| Database | Persistent data storage, transactional integrity | PostgreSQL 14+ |
| Reverse Proxy | SSL termination, load balancing, static file serving | Nginx 1.18+ |
| Service Manager | Process lifecycle, auto-restart, logging | systemd |
| Security Layer | Network filtering, port management | UFW (Uncomplicated Firewall) |

---

## Deployment Strategy

### Deployment Phases

The deployment follows a sequential, automated approach divided into 7 distinct phases:

```mermaid
graph LR
    P0[Phase 0:<br/>Pre-Migration<br/>Preparation] --> P1[Phase 1:<br/>VDS Environment<br/>Setup]
    P1 --> P2[Phase 2:<br/>Database<br/>Configuration]
    P2 --> P3[Phase 3:<br/>Application<br/>Deployment]
    P3 --> P4[Phase 4:<br/>Service<br/>Configuration]
    P4 --> P5[Phase 5:<br/>Infrastructure<br/>Services]
    P5 --> P6[Phase 6:<br/>Validation &<br/>Testing]
    
    style P0 fill:#e1f5ff
    style P1 fill:#fff4e1
    style P2 fill:#ffe1e1
    style P3 fill:#e1ffe1
    style P4 fill:#f0e1ff
    style P5 fill:#ffe1f0
    style P6 fill:#e1ffe1
```

### Phase Breakdown

#### Phase 0: Pre-Migration Preparation (Local Environment)

**Objective**: Prepare the codebase and data for production deployment.

**Activities**:
- Create comprehensive database backup from SQLite
- Clean repository of development artifacts
- Generate PostgreSQL-compatible schema
- Tag Git repository for production release
- Validate all configuration files
- Document environment variables required

**Success Criteria**:
- Database backup created and verified
- All test files and development scripts removed
- Git repository pushed to remote with production tag
- PostgreSQL schema tested locally

#### Phase 1: VDS Environment Setup

**Objective**: Prepare the VDS operating system with all required system packages.

**Automation Script**: `01_vds_setup.sh`

**Activities**:
- System package updates and security patches
- Python 3.11 runtime installation
- PostgreSQL server installation and initialization
- Nginx web server installation
- Certbot SSL certificate manager installation
- UFW firewall configuration

**Infrastructure Decisions**:
- Python 3.11 chosen for modern async support and performance
- PostgreSQL selected over SQLite for production scalability
- Nginx preferred over Apache for better async handling
- UFW provides simple, manageable firewall rules

**Network Security Configuration**:

| Port | Protocol | Purpose | Access |
|------|----------|---------|--------|
| 22 | TCP | SSH administration | Restricted to admin IPs |
| 8080 | TCP | HTTP redirect to HTTPS | Public |
| 443 | TCP | HTTPS web traffic | Public |
| 5432 | TCP | PostgreSQL | Localhost only |
| 8000 | TCP | FastAPI application | Localhost only |

**Success Criteria**:
- All system packages installed without errors
- PostgreSQL service running and enabled
- Nginx service running and enabled
- Firewall active with correct rules
- Python 3.11 available and functional

#### Phase 2: Database Configuration

**Objective**: Create and configure the PostgreSQL database for production use.

**Automation Script**: `02_database_setup.sh`

**Activities**:
- Create production database `kkt_production`
- Create dedicated database user `kkt_user` with limited privileges
- Apply PostgreSQL performance optimizations
- Import database schema from `schema_postgres.sql`
- Configure PostgreSQL authentication
- Set up database connection pooling parameters

**Database Design Decisions**:

**Schema Migration from SQLite to PostgreSQL**:

| SQLite Construct | PostgreSQL Equivalent | Rationale |
|------------------|----------------------|-----------|
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` | PostgreSQL native auto-increment |
| `BOOLEAN DEFAULT 1` | `BOOLEAN DEFAULT TRUE` | Proper boolean type support |
| `julianday()` date functions | PostgreSQL date arithmetic | Native timestamp handling |
| `DATETIME('now')` | `NOW()` or `CURRENT_TIMESTAMP` | Standard SQL compliance |
| File-based locking | Row-level locking | Concurrent transaction support |

**Performance Optimization Parameters**:
- `shared_buffers`: Set to 25% of available RAM
- `effective_cache_size`: Set to 50% of available RAM
- `work_mem`: Configured based on connection count
- `maintenance_work_mem`: Set for efficient index operations
- `max_connections`: Limited to prevent resource exhaustion

**Security Considerations**:
- Database user granted only necessary privileges (no superuser)
- Password authentication required for all connections
- Local connections only (no remote database access)
- SSL enabled for future distributed deployment

**Success Criteria**:
- Database created and accessible
- Schema applied successfully
- Database user can connect with credentials
- Performance parameters configured
- Test query executes successfully

#### Phase 3: Application Deployment

**Objective**: Deploy application code and establish Python runtime environment.

**Automation Script**: `03_app_setup.sh`

**Activities**:
- Clone Git repository to `/home/kktapp/kkt-system`
- Create Python virtual environment with venv
- Install all Python dependencies from requirements files
- Generate .env configuration file from template
- Create application log directories
- Set proper file ownership and permissions
- Validate Python module imports

**Application Structure**:

The deployed application follows this directory structure:

```
/home/kktapp/kkt-system/
├── web/                    # FastAPI web application
│   └── app/
│       ├── main.py         # Application entry point
│       ├── routers/        # API endpoint definitions
│       ├── models/         # Data models
│       └── static/         # Frontend assets
├── bot/                    # Telegram bot application
│   ├── main.py             # Bot entry point
│   ├── handlers/           # Command and callback handlers
│   └── services/           # Business logic services
├── database/               # Database schemas and migrations
├── venv/                   # Python virtual environment
├── .env                    # Environment configuration
├── requirements.txt        # Web app dependencies
└── requirements-web.txt    # Additional web dependencies
```

**Environment Variable Strategy**:

Environment variables are categorized into:

| Category | Variables | Purpose |
|----------|-----------|---------|
| Database | `DATABASE_URL` | PostgreSQL connection string |
| Authentication | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRATION_HOURS` | User session management |
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ADMIN_IDS`, `ADMIN_GROUP_CHAT_ID` | Bot configuration |
| Notifications | `NOTIFICATION_CHECK_TIME`, `NOTIFICATION_TIMEZONE`, `NOTIFICATION_DAYS` | Alert scheduling |
| API Configuration | `API_HOST`, `API_PORT`, `API_RELOAD`, `WEB_API_BASE_URL` | Service endpoints |
| SMTP | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | Email notifications |
| Logging | `LOG_LEVEL`, `LOG_FILE` | Application monitoring |

**Critical Configuration Requirements**:
- `DATABASE_URL` must point to PostgreSQL (not SQLite)
- `JWT_SECRET_KEY` must be cryptographically strong (64+ characters)
- `API_RELOAD` must be `False` in production
- `WEB_API_BASE_URL` should use internal localhost address
- File permissions for .env must be 600 (owner read/write only)

**Dependency Management**:

The system requires two separate dependency files:
- `requirements.txt`: Core application dependencies
- `requirements-web.txt`: Web-specific packages (FastAPI, Uvicorn)
- Additional: `psycopg2-binary` for PostgreSQL connectivity

**Success Criteria**:
- Repository cloned successfully
- Virtual environment created and activated
- All dependencies installed without errors
- .env file created with secure permissions
- Python imports validated for both web and bot applications
- Log directories created with correct ownership

#### Phase 4: Service Configuration

**Objective**: Configure systemd services for automatic application lifecycle management.

**Automation Script**: `04_services_setup.sh`

**Activities**:
- Create systemd unit file for web application
- Create systemd unit file for Telegram bot
- Configure service dependencies and startup order
- Enable automatic restart on failure
- Set resource limits and security constraints
- Enable services for automatic startup on boot

**Systemd Service Design**:

**Web Application Service (`kkt-web.service`)**:

| Configuration | Value | Rationale |
|--------------|-------|-----------|
| Service Type | `notify` | Uvicorn sends readiness notification |
| User | `kktapp` | Non-privileged user for security |
| Working Directory | `/home/kktapp/kkt-system` | Application root |
| Restart Policy | `always` | Automatic recovery from crashes |
| Restart Delay | 10 seconds | Prevent rapid restart loops |
| Dependencies | `postgresql.service` | Ensure database availability |

**Telegram Bot Service (`kkt-bot.service`)**:

| Configuration | Value | Rationale |
|--------------|-------|-----------|
| Service Type | `simple` | Standard long-running process |
| User | `kktapp` | Non-privileged user for security |
| Working Directory | `/home/kktapp/kkt-system` | Application root |
| Restart Policy | `always` | Automatic recovery from crashes |
| Restart Delay | 10 seconds | Prevent rapid restart loops |
| Dependencies | `kkt-web.service` | Bot requires web API availability |

**Service Startup Sequence**:

```mermaid
sequenceDiagram
    participant System Boot
    participant PostgreSQL
    participant Web App
    participant Telegram Bot
    
    System Boot->>PostgreSQL: Start database service
    PostgreSQL->>PostgreSQL: Initialize and ready
    PostgreSQL->>Web App: Dependency satisfied
    Web App->>Web App: Load configuration
    Web App->>Web App: Connect to database
    Web App->>Web App: Start Uvicorn server
    Web App->>Telegram Bot: Dependency satisfied
    Telegram Bot->>Telegram Bot: Initialize bot instance
    Telegram Bot->>Web App: Test API connectivity
    Telegram Bot->>Telegram Bot: Connect to Telegram
    Telegram Bot->>System Boot: All services operational
```

**Resource Isolation and Security**:
- Services run under dedicated non-root user
- Environment variables isolated per service
- Process isolation through systemd cgroups
- Automatic log rotation through journald

**Success Criteria**:
- Both systemd service files created and valid
- Services start without errors
- Service dependencies respected
- Services restart automatically after failure simulation
- Services enabled for boot startup
- Logs accessible through journalctl

#### Phase 5: Infrastructure Services

**Objective**: Configure Nginx reverse proxy and SSL certificate management.

**Automation Script**: `05_nginx_setup.sh`

**Activities**:
- Create Nginx site configuration
- Configure reverse proxy to FastAPI application
- Set up static file serving
- Configure SSL/TLS with Let's Encrypt
- Enable HTTP to HTTPS redirection
- Configure security headers
- Set up log rotation

**Nginx Architecture Design**:

**Request Flow**:

```mermaid
graph LR
    A[Client Request] -->|HTTP :8080| B{Nginx}
    A -->|HTTPS :443| B
    B -->|Redirect 301| C[HTTPS Endpoint]
    C -->|SSL Termination| D{Location Match}
    D -->|/static/| E[Static Files]
    D -->|/* API| F[Proxy to :8000]
    F --> G[FastAPI Application]
    E --> H[Response]
    G --> H
```

**Nginx Configuration Strategy**:

| Directive | Purpose | Implementation |
|-----------|---------|----------------|
| `upstream` | Backend connection pooling | Keep-alive connections to port 8000 |
| `proxy_pass` | Request forwarding | Route dynamic requests to FastAPI |
| `location /static/` | Static file serving | Direct file serving with caching |
| `ssl_certificate` | TLS encryption | Let's Encrypt certificate path |
| `add_header` | Security headers | X-Frame-Options, CSP, etc. |

**SSL/TLS Configuration**:
- Certificate provider: Let's Encrypt (free, automated)
- Certificate renewal: Automatic via certbot cron job
- TLS version: Minimum TLSv1.2
- Cipher suites: Modern, secure ciphers only
- HSTS enabled: Force HTTPS for repeat visitors

**Security Headers Applied**:
- `X-Content-Type-Options: nosniff` - Prevent MIME type sniffing
- `X-Frame-Options: DENY` - Prevent clickjacking
- `X-XSS-Protection: 1; mode=block` - Enable XSS filtering
- `Strict-Transport-Security` - Enforce HTTPS
- `Content-Security-Policy` - Control resource loading

**Static File Optimization**:
- Cache-Control headers: 30-day expiration
- Gzip compression enabled
- ETag support for conditional requests

**Success Criteria**:
- Nginx configuration syntax valid
- SSL certificate obtained and installed
- HTTP requests redirect to HTTPS
- Static files served correctly
- API requests proxied to FastAPI
- Security headers present in responses
- Certificate auto-renewal configured

#### Phase 6: Validation and Testing

**Objective**: Verify all system components function correctly in production configuration.

**Testing Strategy**:

```mermaid
graph TB
    A[Start Testing] --> B[Infrastructure Tests]
    B --> C[Service Health Checks]
    C --> D[API Functionality Tests]
    D --> E[Telegram Bot Tests]
    E --> F[Security Validation]
    F --> G[Performance Baseline]
    G --> H{All Tests Pass?}
    H -->|Yes| I[Deployment Complete]
    H -->|No| J[Debug and Fix]
    J --> B
```

**Test Categories**:

**Infrastructure Tests**:
- Verify all systemd services running
- Confirm PostgreSQL accepting connections
- Check Nginx responding on ports 443 and 8080
- Validate firewall rules active
- Verify SSL certificate valid and trusted

**Service Health Checks**:
- FastAPI `/health` endpoint returns 200
- Database connection pool healthy
- Log files being written correctly
- No critical errors in systemd journal

**API Functionality Tests**:
- User authentication flow (login/logout)
- JWT token generation and validation
- CRUD operations on main entities
- API rate limiting operational
- CORS headers configured correctly

**Telegram Bot Tests**:
- Bot responds to `/start` command
- User registration flow functional
- Notification delivery working
- Command handlers executing correctly
- Error handling graceful

**Security Validation**:
- Non-standard ports not accessible from external
- Database port 5432 not exposed
- .env file permissions restrictive (600)
- No sensitive data in logs
- HTTPS enforced (no plain HTTP access)

**Performance Baseline**:
- API response time under 200ms for standard requests
- Database query performance acceptable
- Memory usage within expected bounds
- No memory leaks detected
- Connection pooling efficient

**Success Criteria**:
- All automated tests pass
- Manual verification successful
- No critical errors in logs
- Performance metrics within acceptable ranges
- Security scan passes

---

## Operational Design

### Backup and Recovery Strategy

**Backup Automation Design**:

**Automation Script**: `06_backup_setup.sh`

**Backup Schedule**:
- Frequency: Daily at 03:00 (low-traffic period)
- Method: PostgreSQL `pg_dump` utility
- Format: Compressed SQL dump (gzip)
- Retention: 7 days of rolling backups
- Storage location: `/home/kktapp/backups/`

**Backup Process Flow**:

```mermaid
sequenceDiagram
    participant Cron
    participant Backup Script
    participant PostgreSQL
    participant File System
    participant Cleanup
    
    Cron->>Backup Script: Trigger at 03:00
    Backup Script->>PostgreSQL: Execute pg_dump
    PostgreSQL->>PostgreSQL: Generate SQL dump
    PostgreSQL->>Backup Script: Return dump data
    Backup Script->>File System: Write compressed archive
    File System->>Backup Script: Confirm write
    Backup Script->>Cleanup: Find old backups
    Cleanup->>File System: Delete backups >7 days
    Cleanup->>Backup Script: Cleanup complete
    Backup Script->>Cron: Success status
```

**Backup File Naming Convention**:
- Pattern: `kkt_backup_YYYYMMDD_HHMMSS.sql.gz`
- Example: `kkt_backup_20251213_030000.sql.gz`

**Recovery Procedures**:

| Scenario | Recovery Method | RTO (Recovery Time Objective) |
|----------|----------------|-------------------------------|
| Data corruption | Restore from latest backup | 15 minutes |
| Accidental deletion | Restore specific tables | 30 minutes |
| Complete system failure | Full system rebuild + restore | 2 hours |
| Database migration error | Rollback to pre-migration backup | 15 minutes |

**Disaster Recovery Plan**:
- Backups stored on same server (local recovery)
- Future enhancement: Off-site backup replication
- Backup integrity verified monthly
- Recovery procedure tested quarterly

### Monitoring and Observability

**Log Management Strategy**:

**Log Sources and Locations**:

| Component | Log Location | Content |
|-----------|-------------|---------|
| Web Application | `journalctl -u kkt-web.service` | Application events, errors, API requests |
| Telegram Bot | `journalctl -u kkt-bot.service` | Bot commands, notifications, errors |
| Nginx Access | `/var/log/nginx/access.log` | HTTP request logs |
| Nginx Errors | `/var/log/nginx/error.log` | Nginx errors, proxy issues |
| PostgreSQL | `/var/log/postgresql/` | Database queries, connections |
| System | `/var/log/syslog` | System-level events |

**Log Rotation Configuration**:
- Rotation frequency: Daily
- Retention period: 30 days
- Compression: Enabled after 1 day
- Max size: 100MB per log file

**Monitoring Metrics**:

| Metric Category | Specific Metrics | Monitoring Method |
|----------------|------------------|-------------------|
| System Resources | CPU usage, RAM usage, disk space | `htop`, `df -h` |
| Service Health | Service status, uptime, restart count | `systemctl status` |
| Application Performance | Response time, error rate, request count | Application logs |
| Database Performance | Connection count, query time, locks | PostgreSQL logs |
| Network | Open connections, bandwidth usage | `netstat`, `iftop` |

**Alert Conditions**:
- Disk space below 10% triggers warning
- Service failure triggers immediate alert
- Error rate above 5% triggers investigation
- Database connection pool exhaustion triggers alert

### Maintenance Procedures

**Routine Maintenance Schedule**:

| Task | Frequency | Responsible Party |
|------|-----------|------------------|
| Check service status | Daily | Automated monitoring |
| Review error logs | Daily | Administrator |
| Verify backups | Weekly | Administrator |
| System updates | Monthly | Administrator |
| Security patches | As released | Administrator |
| Database optimization | Monthly | Database administrator |
| SSL certificate renewal | Automatic (90 days) | Certbot |

**Update and Upgrade Strategy**:

**Application Code Updates**:
1. Pull latest code from Git repository
2. Activate virtual environment
3. Update Python dependencies if changed
4. Run database migrations if required
5. Restart systemd services
6. Verify functionality

**System Package Updates**:
- Security patches: Apply immediately
- Minor updates: Apply monthly during maintenance window
- Major version upgrades: Plan and test thoroughly

**Database Migration Workflow**:
1. Create backup before migration
2. Test migration on staging environment
3. Apply migration during low-traffic period
4. Verify data integrity post-migration
5. Monitor application logs for errors

---

## Security Architecture

### Authentication and Authorization

**Authentication Mechanism**:
- Method: JWT (JSON Web Tokens)
- Token lifetime: 24 hours (configurable)
- Token storage: HTTP-only cookies (web) / memory (bot)
- Algorithm: HS256 (HMAC with SHA-256)

**Authorization Model**:

```mermaid
graph TD
    A[User Request] --> B{Authenticated?}
    B -->|No| C[Return 401 Unauthorized]
    B -->|Yes| D{Role Check}
    D -->|Admin| E[Full Access]
    D -->|User| F[Limited Access]
    D -->|No Role| C
    E --> G[Execute Operation]
    F --> G
```

**Role-Based Access Control**:

| Role | Permissions | Typical Users |
|------|-------------|---------------|
| Admin | Full CRUD, user management, system configuration | System administrators |
| User | View own data, limited edit capabilities | Regular clients |
| Bot | API access for notifications and queries | Telegram bot service account |

**Password Security**:
- Hashing algorithm: bcrypt with cost factor 12
- Password requirements: Minimum 8 characters
- Password storage: Never stored in plain text
- Password reset: Secure token-based flow

### Network Security

**Firewall Rules Design**:

```mermaid
graph LR
    Internet[Internet] -->|Port 443 HTTPS| FW[UFW Firewall]
    Internet -->|Port 8080 HTTP| FW
    Admin[Admin SSH] -->|Port 22| FW
    FW -->|Allow| Nginx[Nginx :443/:8080]
    FW -->|Allow| SSH[SSH :22]
    FW -->|Block| Internal[Internal Ports]
    Nginx -->|Internal| App[FastAPI :8000]
    App -->|Internal| DB[PostgreSQL :5432]
```

**Security Zones**:

| Zone | Components | Access Policy |
|------|-----------|---------------|
| Public | Nginx (443, 8080) | Internet-accessible |
| Management | SSH (22) | Restricted to admin IPs |
| Application | FastAPI (8000) | Localhost only |
| Data | PostgreSQL (5432) | Localhost only |

**DDoS Protection Strategy**:
- Nginx rate limiting enabled
- Connection limits per IP
- Request size limits enforced
- Timeout configurations optimized

### Data Security

**Data Protection Measures**:

| Data Type | Protection Method | Implementation |
|-----------|------------------|----------------|
| Passwords | bcrypt hashing | Cost factor 12 |
| JWT secrets | Environment variables | .env file with 600 permissions |
| Database credentials | Environment variables | Restricted file permissions |
| API tokens | Environment variables | Secure storage |
| Backups | File permissions | Owner read-only (400) |

**Sensitive Data Handling**:
- No sensitive data in logs
- Credentials never in Git repository
- Environment variables over hardcoded values
- Secure token transmission over HTTPS only

**Compliance Considerations**:
- Data retention policies documented
- User data deletion procedures defined
- Audit logging for sensitive operations
- Regular security assessment schedule

---

## Configuration Management

### Environment-Specific Configuration

**Configuration Hierarchy**:

```mermaid
graph TD
    A[.env.example<br/>Template] --> B[.env<br/>Production Config]
    C[Default Values<br/>in Code] --> D[Application Runtime]
    B -->|Override| D
    E[Environment Variables<br/>System Level] -->|Override| D
```

**Configuration Priority** (highest to lowest):
1. System environment variables
2. .env file values
3. Application defaults

**Critical Configuration Parameters**:

| Parameter | Development Value | Production Value | Security Impact |
|-----------|------------------|------------------|-----------------|
| `DATABASE_URL` | SQLite file path | PostgreSQL URL | High - credentials exposed |
| `API_RELOAD` | `True` | `False` | Medium - performance |
| `JWT_SECRET_KEY` | Simple test key | 64-char random | Critical - session security |
| `LOG_LEVEL` | `DEBUG` | `INFO` | Low - information disclosure |
| `API_HOST` | `127.0.0.1` | `0.0.0.0` | Medium - network exposure |

### Secrets Management

**Secret Storage Strategy**:
- All secrets in .env file (not in code)
- .env file permissions: 600 (owner read/write only)
- .env file excluded from Git via .gitignore
- Separate .env.example template without real secrets

**Secret Rotation Policy**:
- JWT secret: Rotate every 90 days
- Database password: Rotate every 180 days
- Telegram bot token: Rotate if compromised
- API keys: Rotate annually or on compromise

**Secret Generation Guidelines**:
- Minimum length: 32 characters
- Character set: Alphanumeric + special characters
- Generation method: Cryptographically secure random
- Python command: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

---

## Performance Considerations

### Scalability Design

**Current Architecture Limitations**:
- Single-server deployment (no horizontal scaling)
- Single database instance (no replication)
- File-based session storage (not distributed)

**Vertical Scaling Capacity**:

| Resource | Minimum | Recommended | Maximum Tested |
|----------|---------|-------------|----------------|
| RAM | 2 GB | 4 GB | 8 GB |
| CPU | 1 core | 2 cores | 4 cores |
| Disk | 20 GB | 40 GB | 100 GB |
| Concurrent Users | 10 | 50 | 100 |

**Performance Optimization Strategies**:

**Database Level**:
- Connection pooling configured
- Indexes on frequently queried columns
- Query optimization via EXPLAIN ANALYZE
- Materialized views for complex aggregations

**Application Level**:
- Async request handling (FastAPI + asyncio)
- Database query result caching
- Static file caching in Nginx
- Lazy loading for large datasets

**Network Level**:
- Gzip compression enabled
- HTTP/2 support in Nginx
- CDN integration for static assets (future)
- Connection keep-alive optimization

### Resource Requirements

**Minimum VDS Specifications**:
- OS: Ubuntu 22.04 LTS
- RAM: 2 GB
- CPU: 1 vCPU (2.4 GHz+)
- Storage: 20 GB SSD
- Network: 100 Mbps
- Bandwidth: 1 TB/month

**Recommended VDS Specifications**:
- OS: Ubuntu 22.04 LTS
- RAM: 4 GB
- CPU: 2 vCPU (2.4 GHz+)
- Storage: 40 GB SSD
- Network: 1 Gbps
- Bandwidth: 2 TB/month

**Resource Utilization Estimates**:

| Component | RAM Usage | CPU Usage | Disk Usage |
|-----------|-----------|-----------|------------|
| PostgreSQL | 500 MB | 10-20% | 2-5 GB (data) |
| FastAPI App | 200 MB | 5-15% | 500 MB (code + logs) |
| Telegram Bot | 100 MB | 5-10% | 100 MB (code + logs) |
| Nginx | 50 MB | 2-5% | 50 MB (logs) |
| System (OS) | 500 MB | 5-10% | 8 GB |
| **Total** | **~1.4 GB** | **~30-60%** | **~12 GB** |

---

## Deployment Execution Plan

### Pre-Deployment Checklist

Before initiating deployment, verify the following:

**Local Environment**:
- [ ] Database backup created and verified
- [ ] All code committed to Git repository
- [ ] Git repository pushed to GitHub
- [ ] PostgreSQL schema generated and tested
- [ ] .env.example file updated with all required variables
- [ ] Development artifacts removed from repository

**VDS Requirements**:
- [ ] VDS provisioned with Ubuntu 22.04 LTS
- [ ] Root SSH access available
- [ ] Domain name registered and DNS configured
- [ ] Domain A record pointing to VDS IP address
- [ ] Sufficient resources available (RAM, CPU, disk)

**Credentials Prepared**:
- [ ] PostgreSQL database password generated (strong, 16+ chars)
- [ ] JWT secret key generated (64+ chars)
- [ ] Telegram bot token obtained from @BotFather
- [ ] Telegram admin IDs collected
- [ ] SMTP credentials prepared (if email notifications enabled)

### Deployment Command Sequence

Execute the following commands on the VDS server in order:

**Step 1: Initial Server Access**
```
Purpose: Connect to VDS and prepare deployment directory
Commands:
  - ssh root@VDS_IP_ADDRESS
  - cd /root
  - git clone https://github.com/zhurbarv-hub/Qoders.git
  - cd Qoders/deployment
  - chmod +x *.sh
Expected Outcome: Deployment scripts accessible and executable
```

**Step 2: Environment Setup**
```
Purpose: Install system packages and configure infrastructure
Script: 01_vds_setup.sh
Duration: 10-15 minutes
Command: sudo ./01_vds_setup.sh
Expected Outcome:
  - Python 3.11 installed
  - PostgreSQL installed and running
  - Nginx installed and running
  - Certbot installed
  - UFW firewall configured and active
Verification: Check service status with systemctl status postgresql nginx
```

**Step 3: Application User Creation**
```
Purpose: Create dedicated non-root user for application
Commands:
  - sudo adduser kktapp
  - (Enter password when prompted)
  - (Accept default values for user information)
Expected Outcome: User kktapp created with home directory
```

**Step 4: Database Configuration**
```
Purpose: Create database and user with appropriate permissions
Script: 02_database_setup.sh
Duration: 5 minutes
Preparation: export DB_PASSWORD="YourStrongPassword123"
Command: sudo ./02_database_setup.sh
Expected Outcome:
  - Database kkt_production created
  - User kkt_user created with password
  - Schema applied successfully
  - Performance parameters configured
Verification: psql -U kkt_user -d kkt_production -c "SELECT 1"
```

**Step 5: Application Deployment**
```
Purpose: Clone repository and install application dependencies
Script: 03_app_setup.sh
Duration: 10 minutes
Command: sudo ./03_app_setup.sh
Expected Outcome:
  - Repository cloned to /home/kktapp/kkt-system
  - Python virtual environment created
  - All dependencies installed
  - .env file created from template
  - Log directories created
Post-Script Action: Edit .env file with production values
  Command: sudo nano /home/kktapp/kkt-system/.env
```

**Step 6: Service Configuration**
```
Purpose: Create and enable systemd services
Script: 04_services_setup.sh
Duration: 2 minutes
Command: sudo ./04_services_setup.sh
Expected Outcome:
  - kkt-web.service created and running
  - kkt-bot.service created and running
  - Both services enabled for auto-start
Verification: 
  - sudo systemctl status kkt-web.service
  - sudo systemctl status kkt-bot.service
```

**Step 7: Nginx and SSL Configuration**
```
Purpose: Configure reverse proxy and enable HTTPS
Script: 05_nginx_setup.sh
Duration: 5-7 minutes
Preparation: export DOMAIN="yourdomain.com"
Command: sudo ./05_nginx_setup.sh
Expected Outcome:
  - Nginx site configuration created
  - SSL certificate obtained from Let's Encrypt
  - HTTP redirects to HTTPS
  - Reverse proxy configured
Verification: curl https://yourdomain.com/health
```

**Step 8: Backup Configuration**
```
Purpose: Enable automated daily backups
Script: 06_backup_setup.sh
Duration: 1 minute
Command: sudo ./06_backup_setup.sh
Expected Outcome:
  - Backup script created
  - Cron job scheduled for daily execution
  - Test backup created and verified
Verification: ls -lh /home/kktapp/backups/
```

### Post-Deployment Validation

After deployment completion, perform the following validation steps:

**Service Health Validation**:
```
Purpose: Confirm all services operational
Commands:
  - sudo systemctl status postgresql
  - sudo systemctl status kkt-web.service
  - sudo systemctl status kkt-bot.service
  - sudo systemctl status nginx
Expected: All services showing "active (running)" status
```

**API Functionality Validation**:
```
Purpose: Verify web application responding correctly
Commands:
  - curl http://localhost:8000/health
  - curl https://yourdomain.com/health
Expected: Both return HTTP 200 with health status JSON
```

**Database Connectivity Validation**:
```
Purpose: Confirm database accessible and functional
Command: psql -U kkt_user -d kkt_production -c "SELECT COUNT(*) FROM users"
Expected: Query executes without error
```

**Telegram Bot Validation**:
```
Purpose: Verify bot responding to commands
Actions:
  - Open Telegram and search for bot
  - Send /start command
  - Verify bot responds with welcome message
Expected: Bot responds promptly with formatted message
```

**Security Validation**:
```
Purpose: Confirm security measures active
Commands:
  - sudo ufw status verbose
  - ls -la /home/kktapp/kkt-system/.env
  - curl http://yourdomain.com:5432
Expected:
  - UFW active with correct rules
  - .env file permissions: -rw------- (600)
  - Port 5432 connection refused (not exposed)
```

**Log Verification**:
```
Purpose: Confirm logging operational
Commands:
  - sudo journalctl -u kkt-web.service -n 50
  - sudo journalctl -u kkt-bot.service -n 50
  - sudo tail -n 50 /var/log/nginx/access.log
Expected: Logs present with recent timestamps, no critical errors
```

---

## Troubleshooting Guide

### Common Issues and Resolutions

**Issue: Service Fails to Start**

Symptoms:
- systemctl status shows "failed" state
- Service exits immediately after start attempt

Diagnostic Steps:
1. Check service logs: `sudo journalctl -u SERVICE_NAME -n 100 --no-pager`
2. Verify .env file exists and has correct permissions
3. Confirm database connectivity
4. Check Python import errors

Common Causes and Solutions:

| Cause | Solution |
|-------|----------|
| Missing .env file | Create from .env.example template |
| Incorrect .env permissions | Set to 600: `chmod 600 .env` |
| Database connection refused | Verify PostgreSQL running and credentials correct |
| Python import errors | Reinstall dependencies in virtual environment |
| Port already in use | Identify and stop conflicting process |

**Issue: Database Connection Errors**

Symptoms:
- Application logs show "connection refused" or "authentication failed"
- Cannot connect to PostgreSQL

Diagnostic Steps:
1. Verify PostgreSQL running: `sudo systemctl status postgresql`
2. Test connection manually: `psql -U kkt_user -d kkt_production`
3. Check database user permissions
4. Verify DATABASE_URL format in .env

Common Causes and Solutions:

| Cause | Solution |
|-------|----------|
| PostgreSQL not running | Start service: `sudo systemctl start postgresql` |
| Incorrect password | Reset password in PostgreSQL and update .env |
| Database does not exist | Run 02_database_setup.sh script |
| Connection string malformed | Verify format: `postgresql://user:pass@localhost:5432/dbname` |

**Issue: Nginx 502 Bad Gateway**

Symptoms:
- Web browser shows "502 Bad Gateway" error
- Nginx logs show upstream connection errors

Diagnostic Steps:
1. Verify FastAPI application running: `sudo systemctl status kkt-web.service`
2. Test FastAPI directly: `curl http://localhost:8000/health`
3. Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
4. Verify proxy_pass configuration correct

Common Causes and Solutions:

| Cause | Solution |
|-------|----------|
| FastAPI not running | Restart service: `sudo systemctl restart kkt-web.service` |
| Wrong proxy port | Verify Nginx config points to port 8000 |
| Application crashed | Check application logs for errors and fix |
| Firewall blocking internal | Verify localhost connections allowed |

**Issue: SSL Certificate Errors**

Symptoms:
- Browser shows "Certificate Invalid" warning
- Certbot renewal failures

Diagnostic Steps:
1. Check certificate status: `sudo certbot certificates`
2. Verify domain DNS resolves to correct IP
3. Check Nginx configuration syntax: `sudo nginx -t`
4. Review certbot logs: `sudo tail -f /var/log/letsencrypt/letsencrypt.log`

Common Causes and Solutions:

| Cause | Solution |
|-------|----------|
| Domain DNS not propagated | Wait for DNS propagation (up to 48 hours) |
| Firewall blocking port 80 | Temporarily allow: `sudo ufw allow 80/tcp` |
| Certbot webroot incorrect | Verify webroot path in Nginx config |
| Rate limit exceeded | Wait 1 week or use staging environment |

**Issue: Telegram Bot Not Responding**

Symptoms:
- Bot does not reply to commands
- Bot appears offline in Telegram

Diagnostic Steps:
1. Check bot service status: `sudo systemctl status kkt-bot.service`
2. Review bot logs: `sudo journalctl -u kkt-bot.service -f`
3. Verify bot token correct in .env
4. Test web API accessibility from bot

Common Causes and Solutions:

| Cause | Solution |
|-------|----------|
| Bot service not running | Start service: `sudo systemctl start kkt-bot.service` |
| Invalid bot token | Verify token with @BotFather and update .env |
| Web API not accessible | Verify kkt-web.service running |
| Network connectivity issues | Check internet connectivity and firewall rules |

### Recovery Procedures

**Procedure: Restore from Backup**

When to Use:
- Data corruption detected
- Accidental data deletion
- Failed migration or update

Steps:
1. Stop application services to prevent further writes
   ```
   sudo systemctl stop kkt-web.service
   sudo systemctl stop kkt-bot.service
   ```

2. Identify backup file to restore
   ```
   ls -lh /home/kktapp/backups/
   ```

3. Drop existing database (CAUTION: Data loss)
   ```
   sudo -u postgres psql -c "DROP DATABASE kkt_production"
   sudo -u postgres psql -c "CREATE DATABASE kkt_production OWNER kkt_user"
   ```

4. Restore backup
   ```
   gunzip < /home/kktapp/backups/BACKUP_FILE.sql.gz | psql -U kkt_user -d kkt_production
   ```

5. Verify data integrity
   ```
   psql -U kkt_user -d kkt_production -c "SELECT COUNT(*) FROM users"
   ```

6. Restart services
   ```
   sudo systemctl start kkt-web.service
   sudo systemctl start kkt-bot.service
   ```

7. Test application functionality

**Procedure: Rollback Deployment**

When to Use:
- New deployment causes critical issues
- Application unstable after update

Steps:
1. Stop services
   ```
   sudo systemctl stop kkt-web.service kkt-bot.service
   ```

2. Switch to previous Git commit
   ```
   cd /home/kktapp/kkt-system
   sudo -u kktapp git log --oneline -10
   sudo -u kktapp git checkout PREVIOUS_COMMIT_HASH
   ```

3. Restore database if schema changed (see backup restore procedure)

4. Reinstall dependencies if changed
   ```
   sudo -u kktapp bash -c "source venv/bin/activate && pip install -r requirements.txt"
   ```

5. Restart services
   ```
   sudo systemctl start kkt-web.service kkt-bot.service
   ```

6. Verify system stability

---

## Maintenance and Operations

### Routine Maintenance Tasks

**Daily Tasks** (Automated or Quick Check):

| Task | Method | Duration |
|------|--------|----------|
| Verify services running | `systemctl status kkt-*` | 1 minute |
| Check disk space | `df -h` | 30 seconds |
| Review error logs | `journalctl -p err -since today` | 2 minutes |
| Verify backup completed | Check `/home/kktapp/backups/` for today's file | 30 seconds |

**Weekly Tasks**:

| Task | Method | Duration |
|------|--------|----------|
| Review full application logs | `journalctl -u kkt-web.service -u kkt-bot.service --since "1 week ago"` | 10 minutes |
| Test backup restoration | Restore backup to test database | 15 minutes |
| Check SSL certificate expiry | `sudo certbot certificates` | 2 minutes |
| Verify notification delivery | Monitor Telegram notification logs | 5 minutes |
| Review user activity | Query database for user statistics | 5 minutes |

**Monthly Tasks**:

| Task | Method | Duration |
|------|--------|----------|
| System updates | `sudo apt update && sudo apt upgrade` | 15 minutes |
| Database optimization | `VACUUM ANALYZE` on database | 10 minutes |
| Log rotation verification | Check log file sizes and rotation | 5 minutes |
| Security audit | Review firewall rules, access logs | 30 minutes |
| Performance review | Analyze response times, resource usage | 20 minutes |

**Quarterly Tasks**:

| Task | Method | Duration |
|------|--------|----------|
| Full system backup | Complete VDS snapshot | 30 minutes |
| Disaster recovery test | Simulate failure and restore | 2 hours |
| Security update | Rotate JWT secret, review access controls | 1 hour |
| Capacity planning | Analyze growth trends, resource needs | 1 hour |
| Documentation update | Update operational procedures | 1 hour |

### Update Procedures

**Application Update Workflow**:

```mermaid
sequenceDiagram
    participant Admin
    participant Git
    participant VDS
    participant Services
    participant Users
    
    Admin->>Git: Push code changes
    Admin->>VDS: SSH connect
    VDS->>Services: Stop services
    Services-->>Users: Maintenance mode
    VDS->>Git: Pull latest code
    VDS->>VDS: Run migrations
    VDS->>VDS: Update dependencies
    VDS->>Services: Start services
    Services->>Services: Health check
    Services-->>Users: Service restored
    VDS-->>Admin: Update complete
```

**Detailed Update Steps**:

1. **Prepare for Update**
   - Review changelog for breaking changes
   - Create database backup
   - Notify users of maintenance window
   - Schedule update during low-traffic period

2. **Execute Update**
   ```
   # Connect to VDS
   ssh kktapp@vds-ip
   cd /home/kktapp/kkt-system
   
   # Stop services
   sudo systemctl stop kkt-web.service kkt-bot.service
   
   # Pull latest code
   git pull origin main
   
   # Update dependencies
   source venv/bin/activate
   pip install --upgrade -r requirements.txt
   pip install --upgrade -r requirements-web.txt
   
   # Run database migrations (if any)
   # python manage.py migrate  # Example command
   
   # Restart services
   sudo systemctl start kkt-web.service kkt-bot.service
   ```

3. **Verify Update**
   - Check service status
   - Test critical functionality
   - Monitor logs for errors
   - Verify user access

4. **Rollback if Necessary**
   - Follow rollback procedure if issues detected
   - Restore database backup if needed
   - Notify users of extended maintenance

**System Package Update Procedure**:

```
# Security updates (can be automated)
sudo apt update
sudo apt upgrade -y

# Full system upgrade (requires testing)
sudo apt update
sudo apt full-upgrade

# Reboot if kernel updated
sudo reboot
```

---

## Migration from SQLite to PostgreSQL

### Migration Strategy

The production deployment involves migrating from SQLite (development) to PostgreSQL (production).

**Migration Approach**:
- Schema-first migration (apply PostgreSQL schema)
- Data migration handled separately (if needed)
- No live data expected in initial production deployment
- Future migrations handled via migration scripts

### Schema Transformation Rules

**Data Type Mappings**:

| SQLite Type | PostgreSQL Type | Notes |
|-------------|-----------------|-------|
| `INTEGER` | `INTEGER` | Direct mapping |
| `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` | Auto-incrementing sequence |
| `TEXT` | `TEXT` or `VARCHAR(n)` | TEXT unlimited, VARCHAR with limit |
| `REAL` | `REAL` or `NUMERIC` | NUMERIC for exact precision |
| `BLOB` | `BYTEA` | Binary data |
| `BOOLEAN` (stored as 0/1) | `BOOLEAN` | Native boolean type |
| `DATETIME` (text) | `TIMESTAMP` | Native timestamp |

**Function Migrations**:

| SQLite Function | PostgreSQL Equivalent |
|-----------------|----------------------|
| `datetime('now')` | `NOW()` or `CURRENT_TIMESTAMP` |
| `julianday(date1) - julianday(date2)` | `date1 - date2` (returns interval) |
| `date('now')` | `CURRENT_DATE` |
| `strftime('%Y-%m-%d', datetime)` | `TO_CHAR(datetime, 'YYYY-MM-DD')` |

**Constraint Migrations**:

| SQLite Constraint | PostgreSQL Equivalent |
|------------------|----------------------|
| `UNIQUE (column)` | `UNIQUE (column)` - Same |
| `CHECK (condition)` | `CHECK (condition)` - Same |
| `FOREIGN KEY` | `FOREIGN KEY` - Same, but enforced by default |
| `NOT NULL` | `NOT NULL` - Same |

### Migration Validation

**Post-Migration Checks**:

1. **Schema Validation**
   - Verify all tables created
   - Confirm all indexes exist
   - Check foreign key constraints

2. **Data Validation**
   - Compare row counts between source and destination
   - Validate data integrity constraints
   - Test sample queries

3. **Application Validation**
   - Run application test suite
   - Verify API endpoints functional
   - Test bot commands

4. **Performance Validation**
   - Execute query performance tests
   - Monitor resource utilization
   - Compare against performance baselines

---

## Future Enhancements

### Planned Improvements

**Phase 2 Enhancements** (3-6 months):

| Enhancement | Description | Benefit |
|-------------|-------------|---------|
| Docker containerization | Package application in Docker containers | Simplified deployment, consistency |
| CI/CD pipeline | Automated testing and deployment | Reduced deployment time, fewer errors |
| Prometheus monitoring | Implement metrics collection | Better observability |
| Off-site backup replication | Replicate backups to remote storage | Disaster recovery improvement |
| Redis caching layer | Add Redis for session and data caching | Performance improvement |

**Phase 3 Enhancements** (6-12 months):

| Enhancement | Description | Benefit |
|-------------|-------------|---------|
| Horizontal scaling | Multi-instance deployment with load balancer | Handle increased load |
| Database replication | PostgreSQL streaming replication | High availability |
| CDN integration | Content delivery network for static assets | Global performance improvement |
| Advanced monitoring | ELK stack or similar for log aggregation | Comprehensive monitoring |
| API versioning | Support multiple API versions | Backward compatibility |

### Scalability Roadmap

**Current Capacity**: ~50 concurrent users, single server

**Scaling Milestones**:

```mermaid
graph LR
    A[Current<br/>Single Server<br/>50 users] --> B[Add Redis<br/>100 users]
    B --> C[Add Load Balancer<br/>2 App Servers<br/>200 users]
    C --> D[Add DB Replica<br/>Read Scaling<br/>500 users]
    D --> E[Microservices<br/>1000+ users]
```

**Scaling Decision Points**:

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU usage | >70% sustained | Vertical scaling (upgrade CPU) |
| RAM usage | >80% sustained | Vertical scaling (add RAM) |
| Concurrent connections | >80 | Add Redis, consider horizontal scaling |
| Database load | >60% CPU | Add read replica |
| Response time | >500ms avg | Add caching layer, optimize queries |

---

## Conclusion

This design document provides a comprehensive blueprint for deploying the KKT system to production infrastructure. The deployment strategy emphasizes:

- **Automation**: Minimizing manual steps through scripted deployment
- **Security**: Multi-layered security from network to application level
- **Reliability**: Automated backups, service management, and monitoring
- **Maintainability**: Clear operational procedures and troubleshooting guides
- **Scalability**: Foundation for future growth and enhancements

**Deployment Success Criteria**:
- All services operational and auto-starting
- HTTPS enabled with valid SSL certificate
- Database migrated and functional
- Automated backups configured
- Monitoring and logging operational
- Security measures verified and active

**Estimated Total Deployment Time**: 45-60 minutes (fully automated scripts)

**Next Steps After Deployment**:
1. Complete post-deployment validation checklist
2. Configure monitoring alerts
3. Train administrators on operational procedures
4. Document any environment-specific configurations
5. Plan first scheduled maintenance window
