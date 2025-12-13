# -*- coding: utf-8 -*-
"""
Pydantic схемы для кассовых аппаратов
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date


class CashRegisterBase(BaseModel):
    """Базовая схема для кассового аппарата"""
    user_id: int = Field(..., description="ID владельца (клиента)")
    serial_number: str = Field(..., min_length=1, max_length=50, description="Заводской номер ККТ")
    fiscal_drive_number: str = Field(..., min_length=1, max_length=50, description="Номер фискального накопителя")
    installation_address: Optional[str] = Field(None, description="Адрес установки")
    register_name: str = Field(..., min_length=1, max_length=100, description="Название кассы")


class CashRegisterCreate(CashRegisterBase):
    """Схема для создания кассового аппарата"""
    pass


class CashRegisterUpdate(BaseModel):
    """Схема для обновления кассового аппарата"""
    serial_number: Optional[str] = Field(None, min_length=1, max_length=50)
    fiscal_drive_number: Optional[str] = Field(None, min_length=1, max_length=50)
    installation_address: Optional[str] = None
    register_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class DeadlineShort(BaseModel):
    """Краткая информация о дедлайне для вложенного отображения"""
    id: int
    deadline_type_name: str
    expiration_date: date
    days_until_expiration: int
    status_color: str
    notes: Optional[str] = None
    
    model_config = {"from_attributes": True}


class CashRegisterResponse(CashRegisterBase):
    """Схема ответа с данными кассового аппарата"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class CashRegisterFullResponse(CashRegisterResponse):
    """Полная информация о кассовом аппарате с дедлайнами"""
    user_name: str
    deadlines: List[DeadlineShort] = []
    
    model_config = {"from_attributes": True}


class CashRegisterListResponse(BaseModel):
    """Схема ответа со списком кассовых аппаратов"""
    total: int
    page: int
    limit: int
    cash_registers: List[CashRegisterResponse]


class CashRegisterSearchParams(BaseModel):
    """Параметры поиска кассовых аппаратов"""
    page: int = Field(1, ge=1, description="Номер страницы")
    limit: int = Field(50, ge=1, le=100, description="Элементов на странице")
    user_id: Optional[int] = Field(None, description="Фильтр по ID клиента")
    active_only: bool = Field(True, description="Только активные кассы")
    search: Optional[str] = Field(None, description="Поиск по заводскому номеру, названию или адресу")
