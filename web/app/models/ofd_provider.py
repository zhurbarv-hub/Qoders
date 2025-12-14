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
    name = Column(String(255), nullable=False, unique=True)
    website = Column(String(255))
    support_phone = Column(String(50))
    support_email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    cash_registers = relationship("CashRegister", back_populates="ofd_provider")
    
    def __repr__(self):
        return f"<OFDProvider(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Преобразование в словарь для JSON ответа"""
        return {
            "id": self.id,
            "name": self.name,
            "website": self.website,
            "support_phone": self.support_phone,
            "support_email": self.support_email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
