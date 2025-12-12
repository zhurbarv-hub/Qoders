# -*- coding: utf-8 -*-
"""
Contact Management API Endpoints
CRUD операции для управления контактами клиентов с Telegram уведомлениями
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import string

from backend.database import get_db
from backend.models import Contact, Client
from backend.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
    MessageResponse
)
from backend.dependencies import (
    get_current_active_user,
    get_pagination_params,
    PaginationParams
)

# Create API router
router = APIRouter(prefix="/api/contacts", tags=["Contacts"])


def generate_registration_code(length: int = 8) -> str:
    """
    Генерация случайного кода регистрации
    
    Args:
        length (int): Длина кода
        
    Returns:
        str: Случайный код из букв и цифр (например: A7K9M2P5)
    """
    alphabet = string.ascii_uppercase + string.digits
    # Исключаем похожие символы: O,0,I,1,L
    alphabet = alphabet.replace('O', '').replace('I', '').replace('L', '').replace('0', '').replace('1', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@router.get("", response_model=ContactListResponse, summary="Список контактов")
async def list_contacts(
    pagination: PaginationParams = Depends(get_pagination_params),
    client_id: Optional[int] = None,
    registered_only: bool = False,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить список всех контактов с пагинацией
    
    **Query Parameters:**
    - page: Номер страницы (default: 1)
    - limit: Контактов на странице (default: 50, max: 100)
    - client_id: Фильтр по клиенту (optional)
    - registered_only: Показать только зарегистрированные в Telegram (default: false)
    
    **Response:**
    - total: Общее количество контактов
    - page: Текущая страница
    - limit: Контактов на странице
    - contacts: Массив контактов
    
    **Authentication:**
    Требуется валидный JWT токен
    """
    # Build base query
    query = db.query(Contact)
    
    # Apply client filter
    if client_id:
        query = query.filter(Contact.client_id == client_id)
    
    # Apply registered filter
    if registered_only:
        query = query.filter(Contact.telegram_id.isnot(None))
    
    # Get total count
    total = query.count()
    
    # Apply pagination and sorting
    contacts = query.order_by(Contact.contact_name)\
                   .offset(pagination.offset)\
                   .limit(pagination.limit)\
                   .all()
    
    # Convert to response schema
    contact_responses = [ContactResponse.model_validate(contact) for contact in contacts]
    
    return ContactListResponse(
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        contacts=contact_responses
    )


@router.get("/{contact_id}", response_model=ContactResponse, summary="Получить контакт")
async def get_contact(
    contact_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получить контакт по ID
    
    **Path Parameters:**
    - contact_id: ID контакта
    
    **Response:**
    - Данные контакта со всеми полями
    
    **Errors:**
    - 404 Not Found: Контакт не найден
    
    **Authentication:**
    Требуется валидный JWT токен
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Контакт с ID {contact_id} не найден"
        )
    
    return ContactResponse.model_validate(contact)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Создать контакт")
async def create_contact(
    contact_data: ContactCreate,
    generate_code: bool = True,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создать новый контакт клиента
    
    **Request Body:**
    - client_id: ID клиента (required)
    - contact_name: ФИО контактного лица (required)
    - phone: Телефон (optional, формат +7XXXXXXXXXX)
    - email: Email (optional)
    - notification_days: Дни уведомлений (default: "14,7,3")
    - notifications_enabled: Включены ли уведомления (default: true)
    - notes: Примечания (optional)
    
    **Query Parameters:**
    - generate_code: Сгенерировать код регистрации (default: true)
    
    **Response:**
    - message: Сообщение об успехе
    - id: ID созданного контакта
    
    **Errors:**
    - 400 Bad Request: Ошибки валидации
    - 404 Not Found: Клиент не существует
    
    **Authentication:**
    Требуется валидный JWT токен
    """
    # Проверяем существование клиента
    client = db.query(Client).filter(Client.id == contact_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Клиент с ID {contact_data.client_id} не найден"
        )
    
    # Создаём новый контакт
    new_contact = Contact(**contact_data.model_dump())
    
    # Генерируем код регистрации если требуется
    if generate_code:
        new_contact.registration_code = generate_registration_code()
        new_contact.code_expires_at = datetime.now() + timedelta(hours=24)
    
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    
    return MessageResponse(
        message=f"Контакт '{new_contact.contact_name}' успешно создан. "
                f"Код регистрации: {new_contact.registration_code}" if generate_code else f"Контакт '{new_contact.contact_name}' успешно создан",
        id=new_contact.id
    )


@router.put("/{contact_id}", response_model=MessageResponse, summary="Обновить контакт")
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновить данные контакта
    
    **Path Parameters:**
    - contact_id: ID контакта
    
    **Request Body:**
    Все поля опциональны:
    - contact_name: ФИО
    - phone: Телефон
    - email: Email
    - notification_days: Дни уведомлений
    - notifications_enabled: Включены ли уведомления
    - notes: Примечания
    
    **Response:**
    - message: Сообщение об успехе
    - id: ID обновлённого контакта
    
    **Errors:**
    - 404 Not Found: Контакт не существует
    
    **Authentication:**
    Требуется валидный JWT токен
    """
    # Fetch existing contact
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Контакт с ID {contact_id} не найден"
        )
    
    # Prepare update data (exclude unset fields)
    update_data = contact_data.model_dump(exclude_unset=True)
    
    # Update contact fields
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    
    return MessageResponse(
        message=f"Контакт '{contact.contact_name}' успешно обновлён",
        id=contact.id
    )


@router.delete("/{contact_id}", response_model=MessageResponse, summary="Удалить контакт")
async def delete_contact(
    contact_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удалить контакт (hard delete)
    
    **Path Parameters:**
    - contact_id: ID контакта
    
    **Response:**
    - message: Сообщение об успехе
    
    **Errors:**
    - 404 Not Found: Контакт не существует
    
    **Note:**
    Полное удаление контакта из базы данных
    
    **Authentication:**
    Требуется валидный JWT токен
    """
    # Fetch contact
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Контакт с ID {contact_id} не найден"
        )
    
    contact_name = contact.contact_name
    
    # Delete contact
    db.delete(contact)
    db.commit()
    
    return MessageResponse(
        message=f"Контакт '{contact_name}' успешно удалён"
    )


@router.post("/{contact_id}/regenerate-code", response_model=MessageResponse, summary="Перегенерировать код")
async def regenerate_registration_code(
    contact_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Сгенерировать новый код регистрации для контакта
    
    **Path Parameters:**
    - contact_id: ID контакта
    
    **Response:**
    - message: Сообщение с новым кодом
    - id: ID контакта
    
    **Errors:**
    - 404 Not Found: Контакт не существует
    - 400 Bad Request: Контакт уже зарегистрирован
    
    **Note:**
    Код действителен 24 часа с момента генерации
    
    **Authentication:**
    Требуется валидный JWT токен
    """
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Контакт с ID {contact_id} не найден"
        )
    
    # Проверяем, не зарегистрирован ли уже
    if contact.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Контакт уже зарегистрирован в Telegram (ID: {contact.telegram_id})"
        )
    
    # Генерируем новый код
    contact.registration_code = generate_registration_code()
    contact.code_expires_at = datetime.now() + timedelta(hours=24)
    
    db.commit()
    db.refresh(contact)
    
    return MessageResponse(
        message=f"Новый код регистрации: {contact.registration_code} (действителен до {contact.code_expires_at.strftime('%d.%m.%Y %H:%M')})",
        id=contact.id
    )


# ============================================
# Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("МОДУЛЬ УПРАВЛЕНИЯ КОНТАКТАМИ")
    print("=" * 60)
    
    print("\nДоступные эндпоинты:")
    print("  • GET /api/contacts - Список контактов с пагинацией")
    print("  • GET /api/contacts/{id} - Получить контакт по ID")
    print("  • POST /api/contacts - Создать новый контакт")
    print("  • PUT /api/contacts/{id} - Обновить контакт")
    print("  • DELETE /api/contacts/{id} - Удалить контакт")
    print("  • POST /api/contacts/{id}/regenerate-code - Перегенерировать код")
    
    print("\n" + "=" * 60)
    print("✅ МОДУЛЬ ГОТОВ К ИСПОЛЬЗОВАНИЮ")
    print("=" * 60)
