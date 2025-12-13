"""
Модель для справочника ОФД провайдеров
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class OFDProvider(Base):
    """Модель провайдера ОФД (Оператор Фискальных Данных)"""
    
    __tablename__ = "ofd_providers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(String(200), nullable=False, unique=True, comment="Наименование ОФД")
    inn = Column(String(12), comment="ИНН провайдера")
    website = Column(String(255), comment="Веб-сайт")
    support_phone = Column(String(50), comment="Телефон поддержки")
    is_active = Column(Boolean, nullable=False, default=True, comment="Активен")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="Дата создания")
    
    # Связи
    cash_registers = relationship("CashRegister", back_populates="ofd_provider")
    
    def __repr__(self):
        return f"<OFDProvider(id={self.id}, name='{self.provider_name}')>"
    
    def to_dict(self):
        """Преобразование в словарь для JSON ответа"""
        return {
            "id": self.id,
            "provider_name": self.provider_name,
            "inn": self.inn,
            "website": self.website,
            "support_phone": self.support_phone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
