# -*- coding: utf-8 -*-
"""
Pydantic схемы для клиентов и дедлайнов
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime


# ============================================
# СХЕМЫ ДЛЯ КЛИЕНТОВ
# ============================================

class ClientBase(BaseModel):
    """Базовая схема клиента"""
    name: str = Field(..., min_length=1, max_length=255, description="Название компании")
    inn: str = Field(..., min_length=10, max_length=12, description="ИНН (10 или 12 цифр)")
    contact_person: Optional[str] = Field(None, max_length=255, description="Контактное лицо")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    email: Optional[str] = Field(None, max_length=255, description="Email")
    address: Optional[str] = Field(None, description="Адрес")
    notes: Optional[str] = Field(None, description="Примечания")
    is_active: bool = Field(True, description="Активен ли клиент")
    
    @validator('inn')
    def validate_inn(cls, v):
        """Проверка ИНН"""
        if not v.isdigit():
            raise ValueError('ИНН должен содержать только цифры')
        if len(v) not in [10, 12]:
            raise ValueError('ИНН должен быть длиной 10 или 12 цифр')
        return v


class ClientCreate(ClientBase):
    """Схема для создания клиента"""
    pass


class ClientUpdate(BaseModel):
    """Схема для обновления клиента"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    inn: Optional[str] = Field(None, min_length=10, max_length=12)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('inn')
    def validate_inn(cls, v):
        """Проверка ИНН"""
        if v is not None:
            if not v.isdigit():
                raise ValueError('ИНН должен содержать только цифры')
            if len(v) not in [10, 12]:
                raise ValueError('ИНН должен быть длиной 10 или 12 цифр')
        return v


class ClientResponse(ClientBase):
    """Схема ответа с данными клиента"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """Схема списка клиентов с пагинацией"""
    total: int
    clients: List[ClientResponse]
    page: int
    page_size: int
    total_pages: int


# ============================================
# СХЕМЫ ДЛЯ ТИПОВ ДЕДЛАЙНОВ
# ============================================

class DeadlineTypeBase(BaseModel):
    """Базовая схема типа дедлайна"""
    type_name: str = Field(..., min_length=1, max_length=100, description="Название типа")
    description: Optional[str] = Field(None, description="Описание")
    is_active: bool = Field(True, description="Активен ли тип")


class DeadlineTypeCreate(DeadlineTypeBase):
    """Схема для создания типа дедлайна"""
    pass


class DeadlineTypeResponse(DeadlineTypeBase):
    """Схема ответа с данными типа дедлайна"""
    id: int
    is_system: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# СХЕМЫ ДЛЯ ДЕДЛАЙНОВ
# ============================================

class DeadlineBase(BaseModel):
    """Базовая схема дедлайна"""
    client_id: int = Field(..., gt=0, description="ID клиента")
    deadline_type_id: int = Field(..., gt=0, description="ID типа дедлайна")
    expiration_date: date = Field(..., description="Дата истечения")
    status: str = Field("active", pattern="^(active|expired|cancelled)$", description="Статус")
    notes: Optional[str] = Field(None, description="Примечания")


class DeadlineCreate(DeadlineBase):
    """Схема для создания дедлайна"""
    pass


class DeadlineUpdate(BaseModel):
    """Схема для обновления дедлайна"""
    deadline_type_id: Optional[int] = Field(None, gt=0)
    expiration_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(active|expired|cancelled)$")
    notes: Optional[str] = None


class DeadlineResponse(DeadlineBase):
    """Схема ответа с данными дедлайна"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeadlineDetailResponse(DeadlineResponse):
    """Расширенная схема дедлайна с данными клиента и типа"""
    client_name: str
    client_inn: str
    deadline_type_name: str
    days_until_expiration: Optional[int] = None


class DeadlineListResponse(BaseModel):
    """Схема списка дедлайнов с пагинацией"""
    total: int
    deadlines: List[DeadlineDetailResponse]
    page: int
    page_size: int
    total_pages: int


# ============================================
# СХЕМЫ ДЛЯ СТАТИСТИКИ
# ============================================

class DashboardStats(BaseModel):
    """Схема статистики для дашборда"""
    total_clients: int
    active_clients: int
    total_deadlines: int
    active_deadlines: int
    status_green: int  # > 14 дней
    status_yellow: int  # 7-14 дней
    status_red: int  # 0-7 дней
    status_expired: int  # < 0 дней