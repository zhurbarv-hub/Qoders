# -*- coding: utf-8 -*-
"""
API endpoints для управления клиентами
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math

from ..dependencies import get_db
from ..models.client import Client, Deadline
from ..models.cash_register import CashRegister
from ..models.user import User
from ..models.client_schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListResponse,
    ClientFullDetailsResponse,
    CashRegisterShort,
    DeadlineShortForClient
)
from ..services.auth_service import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/clients", tags=["Clients"])
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


@router.get("", response_model=ClientListResponse)
async def get_clients(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Количество записей на странице"),
    search: Optional[str] = Query(None, description="Поиск по названию или ИНН"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить список всех клиентов с пагинацией и фильтрами"""
    
    # Базовый запрос
    query = db.query(Client)
    
    # Применение фильтров
    if is_active is not None:
        query = query.filter(Client.is_active == is_active)
    
    # Поиск
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Client.name.ilike(search_pattern),
                Client.inn.like(search_pattern),
                Client.contact_person.ilike(search_pattern)
            )
        )
    
    # Подсчёт общего количества
    total = query.count()
    
    # Пагинация
    offset = (page - 1) * page_size
    clients = query.order_by(Client.name).offset(offset).limit(page_size).all()
    
    # Расчёт количества страниц
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return ClientListResponse(
        total=total,
        clients=clients,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить данные конкретного клиента"""
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {client_id} не найден"
        )
    
    return client


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создать нового клиента"""
    
    # Проверка прав доступа
    if current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания клиентов"
        )
    
    # Проверка уникальности ИНН
    existing_client = db.query(Client).filter(Client.inn == client_data.inn).first()
    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Клиент с ИНН {client_data.inn} уже существует"
        )
    
    # Проверка уникальности названия
    existing_name = db.query(Client).filter(Client.name == client_data.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Клиент с названием '{client_data.name}' уже существует"
        )
    
    # Создание клиента
    new_client = Client(**client_data.model_dump())
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return new_client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить данные клиента"""
    
    # Проверка прав доступа
    if current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования клиентов"
        )
    
    # Поиск клиента
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {client_id} не найден"
        )
    
    # Проверка уникальности ИНН (если изменяется)
    if client_data.inn and client_data.inn != client.inn:
        existing = db.query(Client).filter(Client.inn == client_data.inn).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Клиент с ИНН {client_data.inn} уже существует"
            )
    
    # Проверка уникальности названия (если изменяется)
    if client_data.name and client_data.name != client.name:
        existing = db.query(Client).filter(Client.name == client_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Клиент с названием '{client_data.name}' уже существует"
            )
    
    # Обновление полей
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удалить клиента"""
    
    # Проверка прав доступа (только админ)
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может удалять клиентов"
        )
    
    # Поиск клиента
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {client_id} не найден"
        )
    
    # Удаление (CASCADE удалит связанные записи)
    db.delete(client)
    db.commit()
    
    return None