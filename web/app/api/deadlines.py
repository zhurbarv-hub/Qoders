# -*- coding: utf-8 -*-
"""
API endpoints для управления дедлайнами
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import date, datetime, timedelta
import math

from ..dependencies import get_db
from ..models.client import Deadline, Client, DeadlineType
from ..models.client_schemas import (
    DeadlineCreate,
    DeadlineUpdate,
    DeadlineResponse,
    DeadlineDetailResponse,
    DeadlineListResponse
)
from ..services.auth_service import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/deadlines", tags=["Deadlines"])
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


def calculate_days_until_expiration(expiration_date: date) -> int:
    """Расчёт дней до истечения"""
    delta = expiration_date - date.today()
    return delta.days


def enrich_deadline_with_details(deadline: Deadline) -> dict:
    """Обогащение данных дедлайна дополнительной информацией"""
    return {
        "id": deadline.id,
        "client_id": deadline.client_id,
        "deadline_type_id": deadline.deadline_type_id,
        "expiration_date": deadline.expiration_date,
        "status": deadline.status,
        "notes": deadline.notes,
        "created_at": deadline.created_at,
        "updated_at": deadline.updated_at,
        "client_name": deadline.client.name if deadline.client else None,
        "client_inn": deadline.client.inn if deadline.client else None,
        "deadline_type_name": deadline.deadline_type.type_name if deadline.deadline_type else None,
        "days_until_expiration": calculate_days_until_expiration(deadline.expiration_date)
    }


@router.get("", response_model=DeadlineListResponse)
async def get_deadlines(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(50, ge=1, le=100, description="Количество записей на странице"),
    client_id: Optional[int] = Query(None, description="Фильтр по клиенту"),
    deadline_type_id: Optional[int] = Query(None, description="Фильтр по типу дедлайна"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    date_from: Optional[date] = Query(None, description="Дата от"),
    date_to: Optional[date] = Query(None, description="Дата до"),
    days_until: Optional[int] = Query(None, description="Истекает через N дней"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить список всех дедлайнов с фильтрами и пагинацией"""
    
    # Базовый запрос с JOIN
    query = db.query(Deadline).join(Client).join(DeadlineType)
    
    # Применение фильтров
    if client_id:
        query = query.filter(Deadline.client_id == client_id)
    
    if deadline_type_id:
        query = query.filter(Deadline.deadline_type_id == deadline_type_id)
    
    if status:
        query = query.filter(Deadline.status == status)
    
    if date_from:
        query = query.filter(Deadline.expiration_date >= date_from)
    
    if date_to:
        query = query.filter(Deadline.expiration_date <= date_to)
    
    # Фильтр по дням до истечения
    if days_until is not None:
        target_date = date.today() + timedelta(days=days_until)
        query = query.filter(
            and_(
                Deadline.expiration_date >= date.today(),
                Deadline.expiration_date <= target_date
            )
        )
    
    # Подсчёт общего количества
    total = query.count()
    
    # Пагинация
    offset = (page - 1) * page_size
    deadlines = query.order_by(Deadline.expiration_date).offset(offset).limit(page_size).all()
    
    # Обогащение данных
    enriched_deadlines = [enrich_deadline_with_details(d) for d in deadlines]
    
    # Расчёт количества страниц
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    return DeadlineListResponse(
        total=total,
        deadlines=enriched_deadlines,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/expiring-soon", response_model=List[DeadlineDetailResponse])
async def get_expiring_soon(
    days: int = Query(14, ge=1, le=90, description="Количество дней"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить дедлайны, истекающие в ближайшие N дней"""
    
    target_date = date.today() + timedelta(days=days)
    
    deadlines = db.query(Deadline).join(Client).join(DeadlineType).filter(
        and_(
            Deadline.status == 'active',
            Deadline.expiration_date >= date.today(),
            Deadline.expiration_date <= target_date
        )
    ).order_by(Deadline.expiration_date).all()
    
    return [enrich_deadline_with_details(d) for d in deadlines]


@router.get("/by-client/{client_id}", response_model=List[DeadlineDetailResponse])
async def get_deadlines_by_client(
    client_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить все дедлайны конкретного клиента"""
    
    # Проверка существования клиента
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {client_id} не найден"
        )
    
    query = db.query(Deadline).join(DeadlineType).filter(Deadline.client_id == client_id)
    
    if not include_inactive:
        query = query.filter(Deadline.status == 'active')
    
    deadlines = query.order_by(Deadline.expiration_date).all()
    
    return [enrich_deadline_with_details(d) for d in deadlines]


@router.get("/{deadline_id}", response_model=DeadlineDetailResponse)
async def get_deadline(
    deadline_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить конкретный дедлайн"""
    
    deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
    
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дедлайн с ID {deadline_id} не найден"
        )
    
    return enrich_deadline_with_details(deadline)


@router.post("", response_model=DeadlineDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_deadline(
    deadline_data: DeadlineCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создать новый дедлайн"""
    
    # Проверка прав доступа
    if current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания дедлайнов"
        )
    
    # Проверка существования клиента
    client = db.query(Client).filter(Client.id == deadline_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {deadline_data.client_id} не найден"
        )
    
    # Проверка существования типа дедлайна
    deadline_type = db.query(DeadlineType).filter(
        DeadlineType.id == deadline_data.deadline_type_id
    ).first()
    if not deadline_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тип дедлайна с ID {deadline_data.deadline_type_id} не найден"
        )
    
    # Создание дедлайна
    new_deadline = Deadline(**deadline_data.model_dump())
    db.add(new_deadline)
    db.commit()
    db.refresh(new_deadline)
    
    # TODO: Отправить уведомление в Telegram
    # await send_telegram_notification(new_deadline, db)
    
    return enrich_deadline_with_details(new_deadline)


@router.put("/{deadline_id}", response_model=DeadlineDetailResponse)
async def update_deadline(
    deadline_id: int,
    deadline_data: DeadlineUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить дедлайн"""
    
    # Проверка прав доступа
    if current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования дедлайнов"
        )
    
    # Поиск дедлайна
    deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дедлайн с ID {deadline_id} не найден"
        )
    
    # Обновление полей
    update_data = deadline_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deadline, field, value)
    
    db.commit()
    db.refresh(deadline)
    
    return enrich_deadline_with_details(deadline)


@router.delete("/{deadline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deadline(
    deadline_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удалить дедлайн"""
    
    # Проверка прав доступа (только админ)
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может удалять дедлайны"
        )
    
    # Поиск дедлайна
    deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дедлайн с ID {deadline_id} не найден"
        )
    
    # Удаление
    db.delete(deadline)
    db.commit()
    
    return None