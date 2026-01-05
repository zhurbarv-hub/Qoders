# -*- coding: utf-8 -*-
"""
API endpoints для управления обращениями клиентов
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field
import jwt
from jwt.exceptions import InvalidTokenError

from ..dependencies import get_db
from ..config import settings
from backend.models import SupportRequest, User

router = APIRouter(prefix="/api/support-requests", tags=["support_requests"])
security = HTTPBearer()


# Функция проверки токена аутентификации
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Проверка JWT токена и получение текущего пользователя
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось валидировать токен"
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось валидировать токен"
        )
    
    # Здесь возвращаем объект с ролью для проверки прав
    # В реальности нужно загружать пользователя из БД
    return {"username": username, "role": payload.get("role", "viewer")}


# Pydantic схемы
class SupportRequestBase(BaseModel):
    """Базовая схема обращения"""
    subject: str = Field(..., min_length=1, max_length=255, description="Тема обращения")
    message: str = Field(..., min_length=1, description="Текст обращения")
    contact_phone: str = Field(..., min_length=1, max_length=50, description="Телефон для связи")


class SupportRequestCreate(SupportRequestBase):
    """Схема создания обращения"""
    client_id: int = Field(..., description="ID клиента")


class SupportRequestUpdate(BaseModel):
    """Схема обновления обращения"""
    status: Optional[str] = Field(None, description="Статус обращения")
    resolution_notes: Optional[str] = Field(None, description="Заметки о решении")


class SupportRequestResponse(SupportRequestBase):
    """Схема ответа с обращением"""
    id: int
    client_id: int
    status: str
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    
    # Информация о клиенте
    client_name: Optional[str] = None
    client_company: Optional[str] = None
    client_inn: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[SupportRequestResponse])
async def get_support_requests(
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу"),
    client_id: Optional[int] = Query(None, description="Фильтр по клиенту"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Получить список обращений
    
    Доступно только для администраторов и менеджеров
    """
    # Проверка прав доступа
    if current_user.get("role") not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра обращений"
        )
    
    # Базовый запрос
    query = db.query(SupportRequest).options(
        joinedload(SupportRequest.client)
    )
    
    # Применяем фильтры
    if status_filter:
        query = query.filter(SupportRequest.status == status_filter)
    
    if client_id:
        query = query.filter(SupportRequest.client_id == client_id)
    
    # Сортировка по дате создания (новые сверху)
    query = query.order_by(SupportRequest.created_at.desc())
    
    # Пагинация
    requests = query.offset(skip).limit(limit).all()
    
    # Формируем ответ с информацией о клиенте
    result = []
    for req in requests:
        req_dict = {
            'id': req.id,
            'client_id': req.client_id,
            'subject': req.subject,
            'message': req.message,
            'contact_phone': req.contact_phone,
            'status': req.status,
            'resolution_notes': req.resolution_notes,
            'created_at': req.created_at,
            'updated_at': req.updated_at,
            'resolved_at': req.resolved_at,
            'client_name': req.client.full_name if req.client else None,
            'client_company': req.client.company_name if req.client else None,
            'client_inn': req.client.inn if req.client else None
        }
        result.append(req_dict)
    
    return result


@router.get("/{request_id}", response_model=SupportRequestResponse)
async def get_support_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Получить обращение по ID
    """
    # Проверка прав доступа
    if current_user.get("role") not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра обращений"
        )
    
    support_request = db.query(SupportRequest).options(
        joinedload(SupportRequest.client)
    ).filter(SupportRequest.id == request_id).first()
    
    if not support_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Обращение с ID {request_id} не найдено"
        )
    
    # Формируем ответ
    return {
        'id': support_request.id,
        'client_id': support_request.client_id,
        'subject': support_request.subject,
        'message': support_request.message,
        'contact_phone': support_request.contact_phone,
        'status': support_request.status,
        'resolution_notes': support_request.resolution_notes,
        'created_at': support_request.created_at,
        'updated_at': support_request.updated_at,
        'resolved_at': support_request.resolved_at,
        'client_name': support_request.client.full_name if support_request.client else None,
        'client_company': support_request.client.company_name if support_request.client else None,
        'client_inn': support_request.client.inn if support_request.client else None
    }


@router.patch("/{request_id}", response_model=SupportRequestResponse)
async def update_support_request(
    request_id: int,
    update_data: SupportRequestUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Обновить статус обращения и добавить заметки
    
    Доступно только для администраторов и менеджеров
    """
    # Проверка прав доступа
    if current_user.get("role") not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для изменения обращений"
        )
    
    support_request = db.query(SupportRequest).filter(
        SupportRequest.id == request_id
    ).first()
    
    if not support_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Обращение с ID {request_id} не найдено"
        )
    
    # Обновляем поля
    if update_data.status is not None:
        # Проверка валидного статуса
        valid_statuses = ['new', 'in_progress', 'resolved', 'closed']
        if update_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недопустимый статус. Разрешённые: {', '.join(valid_statuses)}"
            )
        
        support_request.status = update_data.status
        
        # Если статус resolved, устанавливаем время решения
        if update_data.status == 'resolved' and not support_request.resolved_at:
            support_request.resolved_at = datetime.now()
    
    if update_data.resolution_notes is not None:
        support_request.resolution_notes = update_data.resolution_notes
    
    db.commit()
    db.refresh(support_request)
    
    # Загружаем клиента
    db.refresh(support_request, ['client'])
    
    return {
        'id': support_request.id,
        'client_id': support_request.client_id,
        'subject': support_request.subject,
        'message': support_request.message,
        'contact_phone': support_request.contact_phone,
        'status': support_request.status,
        'resolution_notes': support_request.resolution_notes,
        'created_at': support_request.created_at,
        'updated_at': support_request.updated_at,
        'resolved_at': support_request.resolved_at,
        'client_name': support_request.client.full_name if support_request.client else None,
        'client_company': support_request.client.company_name if support_request.client else None,
        'client_inn': support_request.client.inn if support_request.client else None
    }


@router.delete("/{request_id}")
async def delete_support_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Удалить обращение
    
    Доступно только для администраторов
    """
    # Проверка прав доступа - только администраторы
    if current_user.get("role") != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут удалять обращения"
        )
    
    support_request = db.query(SupportRequest).filter(
        SupportRequest.id == request_id
    ).first()
    
    if not support_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Обращение с ID {request_id} не найдено"
        )
    
    db.delete(support_request)
    db.commit()
    
    return {"message": f"Обращение #{request_id} успешно удалено"}


@router.get("/stats/summary")
async def get_support_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Получить статистику по обращениям
    
    Доступно только для администраторов и менеджеров
    """
    # Проверка прав доступа
    if current_user.get("role") not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра статистики"
        )
    
    # Подсчёт по статусам
    total = db.query(SupportRequest).count()
    new_count = db.query(SupportRequest).filter(SupportRequest.status == 'new').count()
    in_progress = db.query(SupportRequest).filter(SupportRequest.status == 'in_progress').count()
    resolved = db.query(SupportRequest).filter(SupportRequest.status == 'resolved').count()
    closed = db.query(SupportRequest).filter(SupportRequest.status == 'closed').count()
    
    return {
        "total": total,
        "new": new_count,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed
    }
