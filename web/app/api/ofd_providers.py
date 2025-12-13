# -*- coding: utf-8 -*-
"""
API для работы со справочником ОФД провайдеров
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from ..dependencies import get_db
from ..models import OFDProvider


router = APIRouter(prefix="/api", tags=["OFD Providers"])


# Pydantic схемы
class OFDProviderResponse(BaseModel):
    """Схема ответа для ОФД провайдера"""
    id: int
    provider_name: str
    inn: str | None = None
    website: str | None = None
    support_phone: str | None = None
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/ofd-providers", response_model=List[OFDProviderResponse])
async def get_ofd_providers(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Получить список ОФД провайдеров
    
    Args:
        active_only: Возвращать только активных провайдеров (по умолчанию True)
        db: Сессия базы данных
        
    Returns:
        Список ОФД провайдеров
    """
    query = db.query(OFDProvider)
    
    if active_only:
        query = query.filter(OFDProvider.is_active == True)
    
    providers = query.order_by(OFDProvider.provider_name).all()
    
    return providers


@router.get("/ofd-providers/{provider_id}", response_model=OFDProviderResponse)
async def get_ofd_provider(
    provider_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить информацию об ОФД провайдере по ID
    
    Args:
        provider_id: ID провайдера
        db: Сессия базы данных
        
    Returns:
        Данные ОФД провайдера
        
    Raises:
        HTTPException: 404 если провайдер не найден
    """
    provider = db.query(OFDProvider).filter(OFDProvider.id == provider_id).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="ОФД провайдер не найден")
    
    return provider
