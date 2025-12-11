# -*- coding: utf-8 -*-
"""
API endpoints для дашборда (статистика)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta

from ..dependencies import get_db
from ..models.client import Client, Deadline, DeadlineType, Contact
from ..models.client_schemas import DashboardStats
from ..services.auth_service import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
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


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить статистику для дашборда"""
    
    # Общее количество клиентов
    total_clients = db.query(func.count(Client.id)).scalar()
    
    # Активные клиенты
    active_clients = db.query(func.count(Client.id)).filter(Client.is_active == True).scalar()
    
    # Общее количество дедлайнов
    total_deadlines = db.query(func.count(Deadline.id)).scalar()
    
    # Активные дедлайны
    active_deadlines = db.query(func.count(Deadline.id)).filter(
        Deadline.status == 'active'
    ).scalar()
    
    today = date.today()
    
    # Зелёный статус: > 14 дней
    status_green = db.query(func.count(Deadline.id)).filter(
        and_(
            Deadline.status == 'active',
            Deadline.expiration_date > today + timedelta(days=14)
        )
    ).scalar()
    
    # Жёлтый статус: 7-14 дней
    status_yellow = db.query(func.count(Deadline.id)).filter(
        and_(
            Deadline.status == 'active',
            Deadline.expiration_date > today + timedelta(days=7),
            Deadline.expiration_date <= today + timedelta(days=14)
        )
    ).scalar()
    
    # Красный статус: 0-7 дней
    status_red = db.query(func.count(Deadline.id)).filter(
        and_(
            Deadline.status == 'active',
            Deadline.expiration_date > today,
            Deadline.expiration_date <= today + timedelta(days=7)
        )
    ).scalar()
    
    # Истёкшие: < 0 дней
    status_expired = db.query(func.count(Deadline.id)).filter(
        and_(
            Deadline.status == 'active',
            Deadline.expiration_date < today
        )
    ).scalar()
    
    return DashboardStats(
        total_clients=total_clients or 0,
        active_clients=active_clients or 0,
        total_deadlines=total_deadlines or 0,
        active_deadlines=active_deadlines or 0,
        status_green=status_green or 0,
        status_yellow=status_yellow or 0,
        status_red=status_red or 0,
        status_expired=status_expired or 0
    )