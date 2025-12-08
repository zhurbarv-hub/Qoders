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
    Administrator accounts for web interface access
    
    Attributes:
        id: Unique user identifier
        email: Login email address (unique)
        password_hash: Bcrypt hashed password
        full_name: Administrator full name
        role: User role (admin, manager)
        is_active: Account active status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User Credentials
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User Information
    full_name = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default='admin', index=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Client(Base):
    """
    Client organizations using cash register services
    
    Attributes:
        id: Unique client identifier
        name: Client organization name (unique)
        inn: Tax identification number (10 or 12 digits, unique)
        contact_person: Primary contact person name
        phone: Contact phone number
        email: Contact email address
        address: Physical address
        notes: Additional notes about client
        is_active: Client active status
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    
    Relationships:
        deadlines: Collection of all deadlines for this client (CASCADE DELETE)
        contacts: Collection of Telegram contacts for this client (CASCADE DELETE)
    """
    __tablename__ = "clients"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Client Information
    name = Column(String(255), nullable=False, unique=True, index=True)
    inn = Column(String(12), nullable=False, unique=True, index=True)
    contact_person = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    deadlines = relationship("Deadline", back_populates="client", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="client", cascade="all, delete-orphan")
    
    # Check Constraints
    __table_args__ = (
        CheckConstraint('length(inn) IN (10, 12)', name='check_inn_length'),
        Index('ix_clients_active_name', 'is_active', 'name'),
    )
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', inn='{self.inn}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'inn': self.inn,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


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
        client_id: Reference to clients.id
        deadline_type_id: Reference to deadline_types.id
        expiration_date: Service expiration date
        status: Deadline status (active, expired, renewed)
        notes: Additional notes
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    
    Relationships:
        client: Reference to parent client record
        deadline_type: Reference to service type
        notification_logs: Collection of notifications for this deadline (CASCADE DELETE)
    """
    __tablename__ = "deadlines"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    deadline_type_id = Column(Integer, ForeignKey('deadline_types.id', ondelete='RESTRICT'), nullable=False, index=True)
    
    # Deadline Information
    expiration_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default='active', index=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="deadlines")
    deadline_type = relationship("DeadlineType", back_populates="deadlines")
    notification_logs = relationship("NotificationLog", back_populates="deadline", cascade="all, delete-orphan")
    
    # Composite Indexes
    __table_args__ = (
        Index('ix_deadlines_status_expiration', 'status', 'expiration_date'),
        Index('ix_deadlines_client_expiration', 'client_id', 'expiration_date'),
    )
    
    def __repr__(self):
        return f"<Deadline(id={self.id}, client_id={self.client_id}, expiration_date='{self.expiration_date}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'client_id': self.client_id,
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


class Contact(Base):
    """
    Telegram contact information for notification delivery
    
    Attributes:
        id: Unique contact identifier
        client_id: Reference to clients.id
        telegram_id: Telegram user ID (unique)
        telegram_username: Telegram username
        first_name: User's first name from Telegram
        last_name: User's last name from Telegram
        notifications_enabled: Notification preference
        registered_at: Registration timestamp
        last_interaction: Last bot interaction timestamp
    
    Relationships:
        client: Reference to parent client record
    """
    __tablename__ = "contacts"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Telegram Information
    telegram_id = Column(String(50), nullable=False, unique=True, index=True)
    telegram_username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Notification Settings
    notifications_enabled = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    registered_at = Column(DateTime, nullable=False, server_default=func.now())
    last_interaction = Column(DateTime, nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="contacts")
    
    # Composite Index
    __table_args__ = (
        Index('ix_contacts_client_enabled', 'client_id', 'notifications_enabled'),
    )
    
    def __repr__(self):
        return f"<Contact(id={self.id}, telegram_id='{self.telegram_id}', client_id={self.client_id})>"
    
    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'telegram_id': self.telegram_id,
            'telegram_username': self.telegram_username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'notifications_enabled': self.notifications_enabled,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None
        }


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
