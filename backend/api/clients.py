"""
Client Management API Endpoints for KKT Services Expiration Management System

This module provides CRUD operations for client management:
- GET /api/clients - List clients with pagination and search
- GET /api/clients/{id} - Get single client with details
- POST /api/clients - Create new client
- PUT /api/clients/{id} - Update existing client
- DELETE /api/clients/{id} - Soft delete client
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional

from backend.database import get_db
from backend.models import Client, Deadline, Contact, User
from backend.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientWithDetails,
    ClientListResponse,
    MessageResponse,
    DeadlineResponse,
    ContactResponse
)
from backend.dependencies import (
    get_current_active_user,
    get_pagination_params,
    get_client_filter_params,
    PaginationParams,
    ClientFilterParams
)


# Create API router
router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.get("", response_model=ClientListResponse, summary="List Clients")
async def list_clients(
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: ClientFilterParams = Depends(get_client_filter_params),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve paginated list of clients with optional filtering
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 50, max: 100)
    - search: Search by name or INN (optional)
    - active_only: Filter only active clients (default: true)
    
    **Response:**
    - total: Total number of matching clients
    - page: Current page number
    - limit: Items per page
    - clients: Array of client objects
    
    **Authentication:**
    Requires valid JWT token
    """
    # Build base query
    query = db.query(Client)
    
    # Apply active filter
    if filters.active_only:
        query = query.filter(Client.is_active == True)
    
    # Apply search filter
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.filter(
            or_(
                Client.name.ilike(search_term),
                Client.inn.like(search_term)
            )
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    clients = query.order_by(Client.name)\
                   .offset(pagination.offset)\
                   .limit(pagination.limit)\
                   .all()
    
    # Convert to response schema
    client_responses = [ClientResponse.model_validate(client) for client in clients]
    
    return ClientListResponse(
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        clients=client_responses
    )


@router.get("/{client_id}", response_model=ClientWithDetails, summary="Get Client by ID")
async def get_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve single client with full details including deadlines and contacts
    
    **Path Parameters:**
    - client_id: Client ID to fetch
    
    **Response:**
    - Client object with nested:
      - deadlines: Array of active deadlines with calculated fields
      - contacts: Array of Telegram contacts
    
    **Errors:**
    - 404 Not Found: Client does not exist
    
    **Authentication:**
    Requires valid JWT token
    """
    # Query client with eager loading
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Convert to response with details
    client_dict = client.to_dict()
    
    # Add deadlines with calculated fields
    deadlines = []
    for deadline in client.deadlines:
        deadline_dict = deadline.to_dict()
        deadline_dict['days_until_expiration'] = deadline.days_until_expiration
        deadline_dict['status_color'] = deadline.status_color
        deadline_dict['deadline_type_name'] = deadline.deadline_type.type_name if deadline.deadline_type else None
        deadlines.append(DeadlineResponse(**deadline_dict))
    
    # Add contacts
    contacts = [ContactResponse.model_validate(contact) for contact in client.contacts]
    
    client_dict['deadlines'] = deadlines
    client_dict['contacts'] = contacts
    
    return ClientWithDetails(**client_dict)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Create Client")
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new client record
    
    **Request Body:**
    - name: Client organization name (required, unique)
    - inn: Tax identification number (required, unique, 10 or 12 digits)
    - contact_person: Primary contact name (optional)
    - phone: Contact phone number (optional, Russian format)
    - email: Contact email address (optional)
    - address: Physical address (optional)
    - notes: Additional notes (optional)
    
    **Validation:**
    - Name must be unique
    - INN must be unique and exactly 10 or 12 digits
    - Phone must match Russian format if provided: +7XXXXXXXXXX
    - Email must be valid format if provided
    
    **Response:**
    - message: Success message
    - id: New client ID
    
    **Errors:**
    - 400 Bad Request: Validation errors
    - 409 Conflict: Duplicate INN or name
    
    **Authentication:**
    Requires valid JWT token
    """
    # Check for duplicate INN
    existing_inn = db.query(Client).filter(Client.inn == client_data.inn).first()
    if existing_inn:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Client with INN {client_data.inn} already exists"
        )
    
    # Check for duplicate name
    existing_name = db.query(Client).filter(Client.name == client_data.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Client with name '{client_data.name}' already exists"
        )
    
    # Create new client
    new_client = Client(**client_data.model_dump())
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return MessageResponse(
        message="Client created successfully",
        id=new_client.id
    )


@router.put("/{client_id}", response_model=MessageResponse, summary="Update Client")
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update existing client record
    
    **Path Parameters:**
    - client_id: Client ID to update
    
    **Request Body:**
    All fields optional:
    - name: Client organization name (must be unique if changed)
    - inn: Tax identification number (must be unique if changed)
    - contact_person: Primary contact name
    - phone: Contact phone number
    - email: Contact email address
    - address: Physical address
    - notes: Additional notes
    - is_active: Active status
    
    **Response:**
    - message: Success message
    - id: Updated client ID
    
    **Errors:**
    - 404 Not Found: Client does not exist
    - 409 Conflict: Duplicate INN or name
    
    **Authentication:**
    Requires valid JWT token
    """
    # Fetch existing client
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Prepare update data (exclude unset fields)
    update_data = client_data.model_dump(exclude_unset=True)
    
    # Check for duplicate INN if being changed
    if 'inn' in update_data and update_data['inn'] != client.inn:
        existing_inn = db.query(Client).filter(
            Client.inn == update_data['inn'],
            Client.id != client_id
        ).first()
        if existing_inn:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Client with INN {update_data['inn']} already exists"
            )
    
    # Check for duplicate name if being changed
    if 'name' in update_data and update_data['name'] != client.name:
        existing_name = db.query(Client).filter(
            Client.name == update_data['name'],
            Client.id != client_id
        ).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Client with name '{update_data['name']}' already exists"
            )
    
    # Update client fields
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    return MessageResponse(
        message="Client updated successfully",
        id=client.id
    )


@router.delete("/{client_id}", response_model=MessageResponse, summary="Delete Client")
async def delete_client(
    client_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete client (sets is_active to False)
    
    **Path Parameters:**
    - client_id: Client ID to delete
    
    **Behavior:**
    - Sets is_active = False (soft delete)
    - Preserves all data for audit trail
    - Associated deadlines remain in database
    - Client excluded from active queries
    
    **Response:**
    - message: Success message
    
    **Errors:**
    - 404 Not Found: Client does not exist
    
    **Note:**
    For hard delete with CASCADE removal of deadlines and contacts,
    admin can use database tools directly
    
    **Authentication:**
    Requires valid JWT token
    """
    # Fetch client
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {client_id} not found"
        )
    
    # Soft delete
    client.is_active = False
    
    db.commit()
    
    return MessageResponse(
        message=f"Client '{client.name}' deactivated successfully"
    )


# ============================================
# Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("МОДУЛЬ УПРАВЛЕНИЯ КЛИЕНТАМИ")
    print("=" * 60)
    
    print("\nДоступные эндпоинты:")
    print("  • GET /api/clients - Список клиентов с пагинацией")
    print("  • GET /api/clients/{id} - Получить клиента с деталями")
    print("  • POST /api/clients - Создать нового клиента")
    print("  • PUT /api/clients/{id} - Обновить клиента")
    print("  • DELETE /api/clients/{id} - Удалить клиента (soft delete)")
    
    print("\n" + "=" * 60)
    print("✅ МОДУЛЬ ГОТОВ К ИСПОЛЬЗОВАНИЮ")
    print("=" * 60)
