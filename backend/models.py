"""
SQLAlchemy Database Models for KKT Services Expiration Management System

This module defines all database tables as SQLAlchemy ORM models.
Each model represents a table and includes column definitions, relationships,
constraints, and automatic timestamp management.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class User(Base):
    """
    Unified user accounts for all system users (clients, managers, administrators)
    
    This model combines what was previously separated into users, clients, and contacts.
    All system participants are now users with different roles:
    - 'client': Organization clients (have inn, company_name, can use Telegram)
    - 'manager': Support team members with limited admin rights
    - 'admin': Full system administrators
    
    Attributes:
        id: Unique user identifier
        email: Login email address (unique)
        password_hash: Bcrypt hashed password (NULL for clients not yet registered)
        full_name: User's full name or contact person name
        role: User role (client, manager, admin)
        
        # Client-specific fields (NULL for managers/admins)
        inn: Tax identification number (10 or 12 digits, unique)
        company_name: Organization name for clients
        
        # Contact information (for all users)
        phone: Contact phone number
        address: Physical address
        notes: Additional notes
        
        # Telegram integration (primarily for clients)
        telegram_id: Telegram user ID (unique)
        telegram_username: Telegram username
        registration_code: One-time registration code
        code_expires_at: Registration code expiration
        first_name: First name from Telegram
        last_name: Last name from Telegram
        
        # Notification settings (only for clients)
        notification_days: Comma-separated days for notifications (e.g. '30,14,7,3')
        notifications_enabled: Enable/disable notifications
        
        # Status and metadata
        is_active: Account active status
        registered_at: Registration timestamp
        last_interaction: Last activity timestamp
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    
    Relationships:
        deadlines: Collection of all deadlines for this user (CASCADE DELETE)
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Authentication
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL for clients not yet registered
    
    # Common fields
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='client', index=True)
    
    # Client-specific fields (NULL for managers/admins)
    inn = Column(String(12), nullable=True, unique=True, index=True)
    company_name = Column(String(255), nullable=True)
    
    # Contact information (for all users)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Telegram integration
    telegram_id = Column(String(50), nullable=True, unique=True, index=True)
    telegram_username = Column(String(100), nullable=True)
    registration_code = Column(String(20), nullable=True, unique=True)
    code_expires_at = Column(DateTime, nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Notification settings (for clients)
    notification_days = Column(String(100), nullable=False, default='14,7,3')
    notifications_enabled = Column(Boolean, nullable=False, default=True)
    
    # Status and metadata
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    registered_at = Column(DateTime, nullable=False, server_default=func.now())
    last_interaction = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    deadlines = relationship("Deadline", back_populates="user", cascade="all, delete-orphan")
    
    # Check Constraints
    __table_args__ = (
        CheckConstraint("role IN ('client', 'manager', 'admin')", name='check_role'),
        CheckConstraint('inn IS NULL OR length(inn) IN (10, 12)', name='check_inn_length'),
        Index('ix_users_role_active', 'role', 'is_active'),
    )
    
    # Helper Properties
    
    @property
    def notification_days_list(self):
        """Parse notification_days string to list of integers"""
        if not self.notification_days:
            return [14, 7, 3]
        try:
            return [int(day.strip()) for day in self.notification_days.split(',') if day.strip()]
        except (ValueError, AttributeError):
            return [14, 7, 3]
    
    @property
    def is_registered(self):
        """Check if user has completed registration (has password or telegram_id)"""
        return (self.password_hash is not None and len(str(self.password_hash).strip()) > 0) or \
               (self.telegram_id is not None and len(str(self.telegram_id).strip()) > 0)
    
    @property
    def is_code_valid(self):
        """Check if registration code hasn't expired"""
        if not self.registration_code or not self.code_expires_at:
            return False
        return datetime.now() < self.code_expires_at
    
    @property
    def is_client(self):
        """Check if user is a client"""
        return self.role == 'client'
    
    @property
    def is_support(self):
        """Check if user is support team (manager or admin)"""
        return self.role in ['manager', 'admin']
    
    @property
    def display_name(self):
        """Get user display name (full_name or company_name for clients)"""
        if self.is_client and self.company_name:
            return f"{self.company_name} ({self.full_name})"
        return self.full_name
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', inn='{self.inn}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'inn': self.inn,
            'company_name': self.company_name,
            'phone': self.phone,
            'address': self.address,
            'notes': self.notes,
            'telegram_id': self.telegram_id,
            'telegram_username': self.telegram_username,
            'registration_code': self.registration_code,
            'code_expires_at': self.code_expires_at.isoformat() if self.code_expires_at else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'notification_days': self.notification_days,
            'notifications_enabled': self.notifications_enabled,
            'is_active': self.is_active,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================
# DEPRECATED MODELS (Replaced by unified User model)
# Kept for reference during migration, will be removed after completion
# ============================================

# class Client(Base):
#     Client organizations using cash register services
#     
#     Attributes:
#         id: Unique client identifier
#         name: Client organization name (unique)
#         inn: Tax identification number (10 or 12 digits, unique)
#         contact_person: Primary contact person name
#         phone: Contact phone number
#         email: Contact email address
#         address: Physical address
#         notes: Additional notes about client
#         is_active: Client active status
#         created_at: Record creation timestamp
#         updated_at: Last update timestamp
#     
#     Relationships:
#         deadlines: Collection of all deadlines for this client (CASCADE DELETE)
#         contacts: Collection of Telegram contacts for this client (CASCADE DELETE)
# End of deprecated Client model


class DeadlineType(Base):
    """
    Service type catalog for deadline categorization
    
    Attributes:
        id: Unique type identifier
        type_name: Service type name (unique)
        description: Detailed type description
        is_system: System-defined type flag (cannot be deleted if True)
        is_active: Type active status
        created_at: Record creation timestamp
    
    Relationships:
        deadlines: Collection of deadlines using this type (RESTRICT DELETE)
    """
    __tablename__ = "deadline_types"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Type Information
    type_name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, nullable=False, default=False)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    deadlines = relationship("Deadline", back_populates="deadline_type")
    
    def __repr__(self):
        return f"<DeadlineType(id={self.id}, type_name='{self.type_name}', is_system={self.is_system})>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'type_name': self.type_name,
            'description': self.description,
            'is_system': self.is_system,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Deadline(Base):
    """
    Service expiration tracking records
    
    Attributes:
        id: Unique deadline identifier
        user_id: Reference to users.id (replaces client_id)
        client_id: Legacy reference to clients.id (kept for migration, will be removed)
        deadline_type_id: Reference to deadline_types.id
        expiration_date: Service expiration date
        status: Deadline status (active, expired, cancelled)
        notes: Additional notes
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    
    Relationships:
        user: Reference to parent user record (client)
        deadline_type: Reference to service type
        notification_logs: Collection of notifications for this deadline (CASCADE DELETE)
    """
    __tablename__ = "deadlines"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    client_id = Column(Integer, nullable=True, index=True)  # Legacy, will be removed after full migration
    deadline_type_id = Column(Integer, ForeignKey('deadline_types.id', ondelete='RESTRICT'), nullable=False, index=True)
    
    # Deadline Information
    expiration_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default='active', index=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="deadlines")
    deadline_type = relationship("DeadlineType", back_populates="deadlines")
    notification_logs = relationship("NotificationLog", back_populates="deadline", cascade="all, delete-orphan")
    
    # Composite Indexes
    __table_args__ = (
        Index('ix_deadlines_status_expiration', 'status', 'expiration_date'),
        Index('ix_deadlines_user_expiration', 'user_id', 'expiration_date'),
    )
    
    def __repr__(self):
        return f"<Deadline(id={self.id}, user_id={self.user_id}, expiration_date='{self.expiration_date}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'client_id': self.client_id,  # Keep for backward compatibility during migration
            'deadline_type_id': self.deadline_type_id,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def days_until_expiration(self):
        """Calculate days remaining until expiration"""
        if not self.expiration_date:
            return None
        delta = self.expiration_date - datetime.now().date()
        return delta.days
    
    @property
    def status_color(self):
        """Calculate status color based on days remaining"""
        days = self.days_until_expiration
        if days is None:
            return 'unknown'
        if days < 0:
            return 'expired'
        elif days < 7:
            return 'red'
        elif days < 14:
            return 'yellow'
        else:
            return 'green'

# DEPRECATED MODEL: Contact - replaced by User model with role='client'
# Kept for reference during migration phase
#
# class Contact(Base):
#     Telegram contact information for notification delivery
#     
#     Attributes:
#         id: Unique contact identifier
#         client_id: Reference to clients.id
#         telegram_id: Telegram user ID (unique)
#         telegram_username: Telegram username
#         first_name: User's first name from Telegram
#         last_name: User's last name from Telegram
#         notifications_enabled: Notification preference
#         registered_at: Registration timestamp
#         last_interaction: Last bot interaction timestamp
#
# End of deprecated Contact model


class NotificationLog(Base):
    """
    Audit trail for all sent notifications
    
    Attributes:
        id: Unique log entry identifier
        deadline_id: Reference to deadlines.id
        recipient_telegram_id: Recipient Telegram user ID
        message_text: Full notification text sent
        status: Delivery status (sent, failed, pending)
        sent_at: Sending timestamp
        error_message: Error details if failed
    
    Relationships:
        deadline: Reference to deadline that triggered notification
    """
    __tablename__ = "notification_logs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    deadline_id = Column(Integer, ForeignKey('deadlines.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Notification Information
    recipient_telegram_id = Column(String(50), nullable=False, index=True)
    message_text = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default='sent', index=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    sent_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    
    # Relationships
    deadline = relationship("Deadline", back_populates="notification_logs")
    
    # Composite Index
    __table_args__ = (
        Index('ix_notification_logs_deadline_sent', 'deadline_id', 'sent_at'),
    )
    
    def __repr__(self):
        return f"<NotificationLog(id={self.id}, deadline_id={self.deadline_id}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'deadline_id': self.deadline_id,
            'recipient_telegram_id': self.recipient_telegram_id,
            'message_text': self.message_text,
            'status': self.status,
            'error_message': self.error_message,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
