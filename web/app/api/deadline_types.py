# -*- coding: utf-8 -*-
"""
API endpoints для управления типами дедлайнов
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..dependencies import get_db
from ..models.client import DeadlineType
from ..models.client_schemas import (
    DeadlineTypeCreate,
    DeadlineTypeResponse
)
from ..services.auth_service import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/deadline-types", tags=["Deadline Types"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получение текущего пользователя из JWT токена"""
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


@router.get("", response_model=List[DeadlineTypeResponse])
async def get_deadline_types(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить список всех типов дедлайнов (только пользовательские, без системных)"""
    query = db.query(DeadlineType)
    
    # Исключаем системные типы
    query = query.filter(DeadlineType.is_system == False)
    
    if not include_inactive:
        query = query.filter(DeadlineType.is_active == True)
    
    types = query.order_by(DeadlineType.type_name).all()
    return types


@router.get("/{type_id}", response_model=DeadlineTypeResponse)
async def get_deadline_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить конкретный тип дедлайна"""
    deadline_type = db.query(DeadlineType).filter(DeadlineType.id == type_id).first()
    
    if not deadline_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тип дедлайна с ID {type_id} не найден"
        )
    
    return deadline_type


@router.post("", response_model=DeadlineTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_deadline_type(
    type_data: DeadlineTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создать новый тип дедлайна"""
    
    # Проверка прав доступа
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может создавать типы дедлайнов"
        )
    
    # Проверка уникальности названия
    existing = db.query(DeadlineType).filter(
        DeadlineType.type_name == type_data.type_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Тип дедлайна '{type_data.type_name}' уже существует"
        )
    
    # Создание типа
    new_type = DeadlineType(**type_data.model_dump())
    db.add(new_type)
    db.commit()
    db.refresh(new_type)
    
    return new_type


@router.put("/{type_id}", response_model=DeadlineTypeResponse)
async def update_deadline_type(
    type_id: int,
    type_data: DeadlineTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить тип дедлайна"""
    
    # Проверка прав доступа
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может редактировать типы дедлайнов"
        )
    
    # Поиск типа
    deadline_type = db.query(DeadlineType).filter(DeadlineType.id == type_id).first()
    if not deadline_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тип дедлайна с ID {type_id} не найден"
        )
    
    # Проверка уникальности названия (если изменяется)
    if type_data.type_name != deadline_type.type_name:
        existing = db.query(DeadlineType).filter(
            DeadlineType.type_name == type_data.type_name
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Тип дедлайна '{type_data.type_name}' уже существует"
            )
    
    # Обновление полей
    update_data = type_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deadline_type, field, value)
    
    db.commit()
    db.refresh(deadline_type)
    
    return deadline_type


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deadline_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удалить тип дедлайна (только если не используется)"""
    
    # Проверка прав доступа
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может удалять типы дедлайнов"
        )
    
    # Поиск типа
    deadline_type = db.query(DeadlineType).filter(DeadlineType.id == type_id).first()
    if not deadline_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тип дедлайна с ID {type_id} не найден"
        )
    
    # Проверка использования
    from ..models.client import Deadline
    deadlines_count = db.query(Deadline).filter(
        Deadline.deadline_type_id == type_id
    ).count()
    
    if deadlines_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невозможно удалить тип: используется в {deadlines_count} дедлайнах. Сначала деактивируйте тип."
        )
    
    # Удаление
    db.delete(deadline_type)
    db.commit()
    
    return None