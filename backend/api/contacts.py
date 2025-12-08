"""
Contact Management API Endpoints for KKT Services Expiration Management System

This module provides endpoints for Telegram contact management:
- GET /api/clients/{client_id}/contacts - List client contacts
- POST /api/clients/{client_id}/contacts - Add contact manually
- PUT /api/contacts/{contact_id} - Update contact
- DELETE /api/contacts/{contact_id} - Remove contact
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Contact, Client, User
from backend.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    MessageResponse
)
from backend.dependencies import get_current_active_user


# Create API router
router = APIRouter(prefix="/api", tags=["Contacts"])


@router.get("/clients/{client_id}/contacts", response_model=List[ContactResponse], summary="List Client Contacts")
async def list_client_contacts(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all Telegram contacts for specific client
    
    **Path Parameters:**
    - client_id: Client ID
    
    **Response:**
    - Array of contact objects with:
      - Telegram ID and username
      - First and last name from Telegram
      - Notification enabled status
      - Registration and last interaction timestamps
    
    **Errors:**
    - 404 Not Found: Client does not exist
    
    **Authentication:**
    Requires valid JWT token
    """
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Get all contacts for this client
    contacts = db.query(Contact)\
                 .filter(Contact.client_id == client_id)\
                 .order_by(Contact.registered_at.desc())\
                 .all()
    
    return [ContactResponse.model_validate(contact) for contact in contacts]


@router.post("/clients/{client_id}/contacts", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Add Contact Manually")
async def add_contact(
    client_id: int,
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Manually add Telegram contact for client
    
    This is an alternative to bot /start registration.
    Administrators can manually link Telegram users to clients.
    
    **Path Parameters:**
    - client_id: Client ID to link contact to
    
    **Request Body:**
    - telegram_id: Telegram user ID (required, numeric, unique)
    - telegram_username: Telegram username (optional)
    - first_name: User's first name (optional)
    - last_name: User's last name (optional)
    
    **Validation:**
    - telegram_id must be unique (one Telegram user per client)
    - telegram_id must be numeric string
    - client_id must reference existing client
    
    **Response:**
    - message: Success message
    - id: New contact ID
    
    **Errors:**
    - 404 Not Found: Client does not exist
    - 409 Conflict: Telegram ID already registered
    
    **Authentication:**
    Requires valid JWT token
    """
    # Verify client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Check for duplicate Telegram ID
    existing_contact = db.query(Contact).filter(
        Contact.telegram_id == contact_data.telegram_id
    ).first()
    
    if existing_contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Telegram ID {contact_data.telegram_id} is already registered to another client"
        )
    
    # Create new contact
    new_contact = Contact(
        client_id=client_id,
        telegram_id=contact_data.telegram_id,
        telegram_username=contact_data.telegram_username,
        first_name=contact_data.first_name,
        last_name=contact_data.last_name,
        notifications_enabled=True
    )
    
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    
    return MessageResponse(
        message=f"Contact added successfully for client '{client.name}'",
        id=new_contact.id
    )


@router.put("/contacts/{contact_id}", response_model=MessageResponse, summary="Update Contact")
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update contact information
    
    **Path Parameters:**
    - contact_id: Contact ID to update
    
    **Request Body:**
    All fields optional:
    - telegram_username: Update username
    - first_name: Update first name
    - last_name: Update last name
    - notifications_enabled: Toggle notifications on/off
    
    **Use Cases:**
    - Update user profile information synced from Telegram
    - Enable/disable notifications for specific contact
    - Update username when user changes it in Telegram
    
    **Response:**
    - message: Success message
    - id: Updated contact ID
    
    **Errors:**
    - 404 Not Found: Contact does not exist
    
    **Authentication:**
    Requires valid JWT token
    """
    # Fetch contact
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found"
        )
    
    # Update fields
    update_data = contact_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    
    return MessageResponse(
        message="Contact updated successfully",
        id=contact.id
    )


@router.delete("/contacts/{contact_id}", response_model=MessageResponse, summary="Remove Contact")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove Telegram contact
    
    **Path Parameters:**
    - contact_id: Contact ID to remove
    
    **Behavior:**
    - Permanently removes contact from database
    - User will no longer receive notifications
    - User can re-register via bot /start command
    
    **Response:**
    - message: Success message
    
    **Errors:**
    - 404 Not Found: Contact does not exist
    
    **Authentication:**
    Requires valid JWT token
    """
    # Fetch contact
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found"
        )
    
    # Store info for response
    telegram_id = contact.telegram_id
    client_name = contact.client.name if contact.client else "Unknown"
    
    # Delete contact
    db.delete(contact)
    db.commit()
    
    return MessageResponse(
        message=f"Contact removed: Telegram ID {telegram_id} from {client_name}"
    )


@router.post("/contacts/{contact_id}/toggle-notifications", response_model=MessageResponse, summary="Toggle Notifications")
async def toggle_notifications(
    contact_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle notification enabled status for contact
    
    **Path Parameters:**
    - contact_id: Contact ID
    
    **Behavior:**
    - Toggles notifications_enabled between True and False
    - If True → False: Contact stops receiving notifications
    - If False → True: Contact resumes receiving notifications
    
    **Response:**
    - message: Success message with new status
    - id: Contact ID
    
    **Errors:**
    - 404 Not Found: Contact does not exist
    
    **Authentication:**
    Requires valid JWT token
    """
    # Fetch contact
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found"
        )
    
    # Toggle notifications
    contact.notifications_enabled = not contact.notifications_enabled
    
    db.commit()
    
    status_text = "enabled" if contact.notifications_enabled else "disabled"
    
    return MessageResponse(
        message=f"Notifications {status_text} for contact",
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
    print("  • GET /api/clients/{client_id}/contacts - Список контактов клиента")
    print("  • POST /api/clients/{client_id}/contacts - Добавить контакт")
    print("  • PUT /api/contacts/{id} - Обновить контакт")
    print("  • DELETE /api/contacts/{id} - Удалить контакт")
    print("  • POST /api/contacts/{id}/toggle-notifications - Переключить уведомления")
    
    print("\n" + "=" * 60)
    print("✅ МОДУЛЬ ГОТОВ К ИСПОЛЬЗОВАНИЮ")
    print("=" * 60)
