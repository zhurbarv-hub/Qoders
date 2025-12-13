# -*- coding: utf-8 -*-
"""
SQLAlchemy модели для клиентов и дедлайнов
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class Client(Base):
    """Модель клиента"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    inn = Column(String(12), nullable=False, unique=True, index=True)
    contact_person = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    notes = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения
    deadlines = relationship("Deadline", back_populates="client", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', inn='{self.inn}')>"


class DeadlineType(Base):
    """Модель типа дедлайна (услуги)"""
    __tablename__ = "deadline_types"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Отношения
    deadlines = relationship("Deadline", back_populates="deadline_type")
    
    def __repr__(self):
        return f"<DeadlineType(id={self.id}, name='{self.type_name}')>"


class Deadline(Base):
    """Модель дедлайна (срока истечения услуги)"""
    __tablename__ = "deadlines"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)  # Новое поле
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=True, index=True)  # Старое поле (для совместимости)
    deadline_type_id = Column(Integer, ForeignKey('deadline_types.id'), nullable=False, index=True)
    cash_register_id = Column(Integer, ForeignKey('cash_registers.id', ondelete='CASCADE'), nullable=True, index=True)  # Связь с кассовым аппаратом
    expiration_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default='active', index=True)
    notes = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения
    # user = relationship("User", back_populates="deadlines")  # Пока не используем, чтобы избежать циркулярных импортов
    client = relationship("Client", back_populates="deadlines")  # Старая связь
    deadline_type = relationship("DeadlineType", back_populates="deadlines")
    cash_register = relationship("CashRegister", back_populates="deadlines")  # Новая связь
    notification_logs = relationship("NotificationLog", back_populates="deadline", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Deadline(id={self.id}, user_id={self.user_id}, client_id={self.client_id}, expiration={self.expiration_date})>"


class Contact(Base):
    """Модель Telegram контакта"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    telegram_id = Column(String(50), nullable=False, unique=True, index=True)
    telegram_username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    notifications_enabled = Column(Boolean, nullable=False, default=True, index=True)
    registered_at = Column(DateTime, nullable=False, server_default=func.now())
    last_interaction = Column(DateTime)
    
    # Отношения
    client = relationship("Client", back_populates="contacts")
    
    def __repr__(self):
        return f"<Contact(id={self.id}, telegram_id='{self.telegram_id}')>"


class NotificationLog(Base):
    """Модель лога уведомлений"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    deadline_id = Column(Integer, ForeignKey('deadlines.id', ondelete='CASCADE'), nullable=False, index=True)
    recipient_telegram_id = Column(String(50), nullable=False)
    message_text = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default='sent', index=True)
    sent_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    error_message = Column(Text)
    
    # Отношения
    deadline = relationship("Deadline", back_populates="notification_logs")
    
    def __repr__(self):
        return f"<NotificationLog(id={self.id}, deadline_id={self.deadline_id}, status='{self.status}')>"