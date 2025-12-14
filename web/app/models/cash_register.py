# -*- coding: utf-8 -*-
"""
SQLAlchemy модель для кассовых аппаратов
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class CashRegister(Base):
    """Модель кассового аппарата (ККТ)"""
    __tablename__ = "cash_registers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    factory_number = Column(String(100))  # Заводской номер
    registration_number = Column(String(100))  # Регистрационный номер
    model = Column(String(100))  # Модель ККТ (ограничение 100 символов)
    fn_number = Column(String(100))  # Номер фискального накопителя
    ofd_provider_id = Column(Integer, ForeignKey('ofd_providers.id'))  # Провайдер ОФД
    ofd_contract_date = Column(Date)  # Дата договора с ОФД
    ofd_expiry_date = Column(Date)  # Дата окончания договора с ОФД
    fn_expiry_date = Column(Date)  # Дата окончания действия ФН
    registration_expiry_date = Column(Date)  # Дата окончания регистрации
    notes = Column(Text)  # Примечание
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Отношения
    client = relationship("User", back_populates="cash_registers", foreign_keys=[client_id])
    ofd_provider = relationship("OFDProvider", back_populates="cash_registers")
    deadlines = relationship("Deadline", back_populates="cash_register", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CashRegister(id={self.id}, factory_number='{self.factory_number}', model='{self.model}')>"
