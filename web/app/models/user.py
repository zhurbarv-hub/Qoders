# -*- coding: utf-8 -*-
"""
Модель пользователя веб-интерфейса
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class WebUser(Base):
    """
    Пользователи веб-интерфейса для аутентификации
    """
    __tablename__ = "web_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(20), nullable=False, default='viewer', index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    telegram_id = Column(String(50), unique=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<WebUser(id={self.id}, username='{self.username}', role='{self.role}')>"


class User(Base):
    """
    Унифицированная модель пользователя (клиенты, менеджеры, админы)
    Объединяет старые таблицы clients, contacts и users
    """
    __tablename__ = "users"
    
    # Первичный ключ
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Аутентификация
    username = Column(String(50), unique=True, nullable=False, index=True)  # Логин (латинские символы)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL для клиентов, которые еще не установили пароль
    
    # Общие поля
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='client', index=True)  # client, manager, admin
    
    # Поля клиента (NULL для managers/admins)
    inn = Column(String(12), unique=True, nullable=True, index=True)  # Только для клиентов
    company_name = Column(String(255), nullable=True)  # Название компании
    
    # Контактная информация (для всех)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Telegram интеграция (главным образом для клиентов)
    telegram_id = Column(String(50), unique=True, nullable=True, index=True)
    telegram_username = Column(String(100), nullable=True)
    registration_code = Column(String(20), unique=True, nullable=True)
    code_expires_at = Column(DateTime, nullable=True)
    first_name = Column(String(100), nullable=True)  # Из Telegram
    last_name = Column(String(100), nullable=True)   # Из Telegram
    
    # Настройки уведомлений (только для клиентов)
    notification_days = Column(Text, default='14,7,3')
    notifications_enabled = Column(Boolean, default=True)
    
    # Статус и метаданные
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    registered_at = Column(DateTime, default=func.now())
    last_interaction = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Связи
    cash_registers = relationship("CashRegister", back_populates="client", foreign_keys="CashRegister.client_id", cascade="all, delete-orphan")
    client_deadlines = relationship("Deadline", foreign_keys="Deadline.client_id", back_populates="client", cascade="all, delete-orphan")
    user_deadlines = relationship("Deadline", foreign_keys="Deadline.user_id", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', company='{self.company_name}')>"