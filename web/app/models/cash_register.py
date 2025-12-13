# -*- coding: utf-8 -*-
"""
SQLAlchemy модель для кассовых аппаратов
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class CashRegister(Base):
    """Модель кассового аппарата (ККТ)"""
    __tablename__ = "cash_registers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    serial_number = Column(String(50), nullable=False, unique=True, index=True)
    fiscal_drive_number = Column(String(50), nullable=False)
    installation_address = Column(Text)
    register_name = Column(String(100), nullable=False)
    ofd_provider_id = Column(Integer, ForeignKey('ofd_providers.id', ondelete='SET NULL'))  # Провайдер ОФД
    notes = Column(Text)  # Примечание
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Отношения
    # user = relationship("User", back_populates="cash_registers")  # Будет добавлено позже
    ofd_provider = relationship("OFDProvider", back_populates="cash_registers")
    deadlines = relationship("Deadline", back_populates="cash_register", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CashRegister(id={self.id}, serial='{self.serial_number}', name='{self.register_name}')>"
