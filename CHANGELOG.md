# Changelog

## [1.0.0] - 2026-01-05

### Added
- Initial production-ready release
- Multi-tenant deployment system with full VDS isolation
- Client Registry Database for tracking deployed instances
- Test environment setup capability
- PostgreSQL database support
- Telegram bot integration for notifications
- Web dashboard for client and deadline management
- Automatic deadline creation for cash registers
- OFD provider management
- Backup and restore functionality
- User authentication and authorization system
- Admin panel for system management

### Infrastructure
- Master Distribution Server on kkt-box.net
- Client Registry Database (kkt_master_registry)
- GitHub-based release distribution
- Deployment automation scripts

### Components
- FastAPI web application
- Telegram bot service
- PostgreSQL database
- Nginx reverse proxy configuration
- Systemd service management

### Security
- bcrypt password hashing
- JWT token authentication
- HTTPS/SSL support
- Firewall configuration
- Isolated test and production environments
