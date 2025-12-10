# -*- coding: utf-8 -*-
"""
Модель пользователя веб-интерфейса
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
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