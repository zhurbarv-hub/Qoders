# -*- coding: utf-8 -*-
"""
API endpoints для экспорта данных
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, Literal
from datetime import datetime
import json
import csv
import io

from ..dependencies import get_db
from ..models.client import Client, Deadline, DeadlineType
from ..services.auth_service import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/export", tags=["Export"])
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


def export_clients_to_json(clients: list) -> str:
    """Экспорт клиентов в JSON формат"""
    data = {
        "export_date": datetime.now().isoformat(),
        "export_type": "clients",
        "total_records": len(clients),
        "data": [
            {
                "id": c.id,
                "name": c.name,
                "inn": c.inn,
                "contact_person": c.contact_person,
                "email": c.email,
                "phone": c.phone,
                "address": c.address,
                "is_active": c.is_active,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None
            }
            for c in clients
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_clients_to_csv(clients: list) -> str:
    """Экспорт клиентов в CSV формат"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow([
        'ID', 'Название', 'ИНН', 'Контактное лицо', 'Email', 
        'Телефон', 'Адрес', 'Статус', 'Дата создания', 'Дата обновления'
    ])
    
    # Данные
    for c in clients:
        writer.writerow([
            c.id,
            c.name,
            c.inn,
            c.contact_person or '',
            c.email or '',
            c.phone or '',
            c.address or '',
            'Активен' if c.is_active else 'Неактивен',
            c.created_at.strftime('%Y-%m-%d %H:%M:%S') if c.created_at else '',
            c.updated_at.strftime('%Y-%m-%d %H:%M:%S') if c.updated_at else ''
        ])
    
    # Добавляем BOM для корректного отображения в Excel
    return '\ufeff' + output.getvalue()


def export_deadlines_to_json(deadlines: list, db: Session) -> str:
    """Экспорт дедлайнов в JSON формат"""
    data = {
        "export_date": datetime.now().isoformat(),
        "export_type": "deadlines",
        "total_records": len(deadlines),
        "data": [
            {
                "id": d.id,
                "client_id": d.client_id,
                "client_name": d.client.name if d.client else None,
                "client_inn": d.client.inn if d.client else None,
                "deadline_type_id": d.deadline_type_id,
                "deadline_type_name": d.deadline_type.type_name if d.deadline_type else None,
                "expiration_date": d.expiration_date.isoformat() if d.expiration_date else None,
                "status": d.status,
                "notes": d.notes,
                "created_at": d.created_at.isoformat() if d.created_at else None,
                "updated_at": d.updated_at.isoformat() if d.updated_at else None
            }
            for d in deadlines
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_deadlines_to_csv(deadlines: list) -> str:
    """Экспорт дедлайнов в CSV формат"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow([
        'ID', 'Клиент', 'ИНН', 'Тип дедлайна', 'Дата истечения', 
        'Статус', 'Примечания', 'Дата создания', 'Дата обновления'
    ])
    
    # Данные
    for d in deadlines:
        writer.writerow([
            d.id,
            d.client.name if d.client else '',
            d.client.inn if d.client else '',
            d.deadline_type.type_name if d.deadline_type else '',
            d.expiration_date.strftime('%Y-%m-%d') if d.expiration_date else '',
            d.status,
            d.notes or '',
            d.created_at.strftime('%Y-%m-%d %H:%M:%S') if d.created_at else '',
            d.updated_at.strftime('%Y-%m-%d %H:%M:%S') if d.updated_at else ''
        ])
    
    # Добавляем BOM для корректного отображения в Excel
    return '\ufeff' + output.getvalue()


@router.get("/clients")
async def export_clients(
    format: Literal["json", "csv"] = Query("json", description="Формат экспорта"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Экспорт клиентов в JSON или CSV формате
    
    - **format**: json или csv
    - **is_active**: true для активных, false для неактивных, null для всех
    """
    
    # Проверка прав доступа
    if current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для экспорта данных"
        )
    
    # Получение данных
    query = db.query(Client)
    
    if is_active is not None:
        query = query.filter(Client.is_active == is_active)
    
    clients = query.order_by(Client.name).all()
    
    # Экспорт в выбранный формат
    if format == "json":
        content = export_clients_to_json(clients)
        media_type = "application/json"
        filename = f"clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:  # csv
        content = export_clients_to_csv(clients)
        media_type = "text/csv"
        filename = f"clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/deadlines")
async def export_deadlines(
    format: Literal["json", "csv"] = Query("json", description="Формат экспорта"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    client_id: Optional[int] = Query(None, description="Фильтр по клиенту"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Экспорт дедлайнов в JSON или CSV формате
    
    - **format**: json или csv
    - **status**: active, inactive или null для всех
    - **client_id**: ID клиента или null для всех
    """
    
    # Проверка прав доступа
    if current_user.get('role') not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для экспорта данных"
        )
    
    # Получение данных с JOIN
    query = db.query(Deadline).join(Client).join(DeadlineType)
    
    if status:
        query = query.filter(Deadline.status == status)
    
    if client_id:
        query = query.filter(Deadline.client_id == client_id)
    
    deadlines = query.order_by(Deadline.expiration_date).all()
    
    # Экспорт в выбранный формат
    if format == "json":
        content = export_deadlines_to_json(deadlines, db)
        media_type = "application/json"
        filename = f"deadlines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:  # csv
        content = export_deadlines_to_csv(deadlines)
        media_type = "text/csv"
        filename = f"deadlines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/statistics")
async def export_statistics(
    format: Literal["json", "csv"] = Query("json", description="Формат экспорта"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Экспорт статистики системы
    
    - **format**: json или csv
    """
    
    # Проверка прав доступа (только админ)
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может экспортировать статистику"
        )
    
    from datetime import date, timedelta
    
    # Сбор статистики
    stats = {}
    
    # Клиенты
    stats['total_clients'] = db.query(Client).count()
    stats['active_clients'] = db.query(Client).filter(Client.is_active == True).count()
    stats['inactive_clients'] = stats['total_clients'] - stats['active_clients']
    
    # Дедлайны
    stats['total_deadlines'] = db.query(Deadline).count()
    stats['active_deadlines'] = db.query(Deadline).filter(Deadline.status == 'active').count()
    stats['inactive_deadlines'] = db.query(Deadline).filter(Deadline.status == 'inactive').count()
    
    # Дедлайны по срокам
    today = date.today()
    all_active = db.query(Deadline).filter(Deadline.status == 'active').all()
    
    green_count = 0
    yellow_count = 0
    red_count = 0
    expired_count = 0
    
    for d in all_active:
        days_remaining = (d.expiration_date - today).days
        if days_remaining < 0:
            expired_count += 1
        elif days_remaining < 7:
            red_count += 1
        elif days_remaining < 14:
            yellow_count += 1
        else:
            green_count += 1
    
    stats['status_green'] = green_count
    stats['status_yellow'] = yellow_count
    stats['status_red'] = red_count
    stats['status_expired'] = expired_count
    
    # Дедлайны по типам
    deadline_types = db.query(DeadlineType).all()
    stats['by_type'] = {}
    for dt in deadline_types:
        count = db.query(Deadline).filter(
            Deadline.deadline_type_id == dt.id,
            Deadline.status == 'active'
        ).count()
        stats['by_type'][dt.type_name] = count
    
    # Формирование ответа
    if format == "json":
        data = {
            "export_date": datetime.now().isoformat(),
            "export_type": "statistics",
            "data": stats
        }
        content = json.dumps(data, ensure_ascii=False, indent=2)
        media_type = "application/json"
        filename = f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    else:  # csv
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['Метрика', 'Значение'])
        writer.writerow(['Всего клиентов', stats['total_clients']])
        writer.writerow(['Активных клиентов', stats['active_clients']])
        writer.writerow(['Неактивных клиентов', stats['inactive_clients']])
        writer.writerow(['Всего дедлайнов', stats['total_deadlines']])
        writer.writerow(['Активных дедлайнов', stats['active_deadlines']])
        writer.writerow(['Неактивных дедлайнов', stats['inactive_deadlines']])
        writer.writerow(['Безопасно (>14 дней)', stats['status_green']])
        writer.writerow(['Внимание (7-14 дней)', stats['status_yellow']])
        writer.writerow(['Критично (<7 дней)', stats['status_red']])
        writer.writerow(['Просрочено', stats['status_expired']])
        
        writer.writerow([])
        writer.writerow(['Дедлайны по типам', ''])
        for type_name, count in stats['by_type'].items():
            writer.writerow([type_name, count])
        
        # Добавляем BOM для корректного отображения в Excel
        content = '\ufeff' + output.getvalue()
        media_type = "text/csv"
        filename = f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )