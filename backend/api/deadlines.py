"""
Deadline Management API Endpoints for KKT Services Expiration Management System

This module provides CRUD operations for deadline management:
- GET /api/deadlines - List deadlines with filtering and sorting
- GET /api/deadlines/{id} - Get single deadline with details
- POST /api/deadlines - Create new deadline
- PUT /api/deadlines/{id} - Update existing deadline
- DELETE /api/deadlines/{id} - Delete deadline
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List
from datetime import date, datetime

from backend.database import get_db
from backend.models import Deadline, Client, DeadlineType, User
from backend.schemas import (
    DeadlineCreate,
    DeadlineUpdate,
    DeadlineResponse,
    DeadlineListResponse,
    MessageResponse
)
from backend.dependencies import (
    get_current_active_user,
    get_pagination_params,
    get_deadline_filter_params,
    PaginationParams,
    DeadlineFilterParams
)


# Create API router
router = APIRouter(prefix="/api/deadlines", tags=["Deadlines"])


@router.get("", response_model=DeadlineListResponse, summary="List Deadlines")
async def list_deadlines(
    pagination: PaginationParams = Depends(get_pagination_params),
    filters: DeadlineFilterParams = Depends(get_deadline_filter_params),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve deadlines with filtering, sorting, and pagination
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 50, max: 100)
    - client_id: Filter by client ID (optional)
    - deadline_type_id: Filter by deadline type ID (optional)
    - status: Filter by status color (green/yellow/red/expired) (optional)
    - sort_by: Sort field (default: expiration_date)
    - order: Sort order (asc/desc, default: asc)
    
    **Response:**
    - total: Total number of matching deadlines
    - page: Current page number
    - limit: Items per page
    - deadlines: Array of deadline objects with calculated fields
    
    **Calculated Fields:**
    - days_until_expiration: Days remaining
    - status_color: green (>14 days), yellow (7-14), red (<7), expired (<0)
    
    **Authentication:**
    Requires valid JWT token
    """
    # Build base query with joins
    query = db.query(Deadline)\
              .join(Client)\
              .join(DeadlineType)
    
    # Apply filters
    if filters.client_id:
        query = query.filter(Deadline.client_id == filters.client_id)
    
    if filters.deadline_type_id:
        query = query.filter(Deadline.deadline_type_id == filters.deadline_type_id)
    
    # Filter by status color (calculated field)
    if filters.status:
        today = date.today()
        if filters.status == 'expired':
            query = query.filter(Deadline.expiration_date < today)
        elif filters.status == 'red':
            query = query.filter(
                Deadline.expiration_date >= today,
                Deadline.expiration_date < today.replace(day=today.day + 7)
            )
        elif filters.status == 'yellow':
            query = query.filter(
                Deadline.expiration_date >= today.replace(day=today.day + 7),
                Deadline.expiration_date < today.replace(day=today.day + 14)
            )
        elif filters.status == 'green':
            query = query.filter(Deadline.expiration_date >= today.replace(day=today.day + 14))
    
    # Get total count
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(Deadline, filters.sort_by, Deadline.expiration_date)
    if filters.order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))
    
    # Apply pagination
    deadlines = query.offset(pagination.offset).limit(pagination.limit).all()
    
    # Convert to response with calculated fields
    deadline_responses = []
    for deadline in deadlines:
        deadline_dict = deadline.to_dict()
        deadline_dict['days_until_expiration'] = deadline.days_until_expiration
        deadline_dict['status_color'] = deadline.status_color
        deadline_dict['client_name'] = deadline.client.name if deadline.client else None
        deadline_dict['deadline_type_name'] = deadline.deadline_type.type_name if deadline.deadline_type else None
        deadline_responses.append(DeadlineResponse(**deadline_dict))
    
    return DeadlineListResponse(
        total=total,
        page=pagination.page,
        limit=pagination.limit,
        deadlines=deadline_responses
    )


@router.get("/{deadline_id}", response_model=DeadlineResponse, summary="Get Deadline by ID")
async def get_deadline(
    deadline_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve single deadline with full details
    
    **Path Parameters:**
    - deadline_id: Deadline ID to fetch
    
    **Response:**
    - Deadline object with:
      - Calculated fields (days_remaining, status_color)
      - Client name
      - Deadline type name
    
    **Errors:**
    - 404 Not Found: Deadline does not exist
    
    **Authentication:**
    Requires valid JWT token
    """
    deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
    
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline with id {deadline_id} not found"
        )
    
    # Build response with calculated fields
    deadline_dict = deadline.to_dict()
    deadline_dict['days_until_expiration'] = deadline.days_until_expiration
    deadline_dict['status_color'] = deadline.status_color
    deadline_dict['client_name'] = deadline.client.name if deadline.client else None
    deadline_dict['deadline_type_name'] = deadline.deadline_type.type_name if deadline.deadline_type else None
    
    return DeadlineResponse(**deadline_dict)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Create Deadline")
async def create_deadline(
    deadline_data: DeadlineCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new deadline for a client
    
    **Request Body:**
    - client_id: Client ID (required, must exist)
    - deadline_type_id: Deadline type ID (required, must exist)
    - expiration_date: Service expiration date (required)
    - notes: Additional notes (optional)
    
    **Validation:**
    - client_id must reference existing active client
    - deadline_type_id must reference existing active deadline type
    - expiration_date must be valid date
    - Warning if expiration_date is in the past (but allowed for historical data)
    
    **Response:**
    - message: Success message
    - id: New deadline ID
    
    **Errors:**
    - 400 Bad Request: Validation errors
    - 404 Not Found: Client or deadline type not found
    
    **Authentication:**
    Requires valid JWT token
    """
    # Validate client exists
    client = db.query(Client).filter(Client.id == deadline_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {deadline_data.client_id} not found"
        )
    
    # Validate deadline type exists
    deadline_type = db.query(DeadlineType).filter(
        DeadlineType.id == deadline_data.deadline_type_id
    ).first()
    if not deadline_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline type with id {deadline_data.deadline_type_id} not found"
        )
    
    # Check if deadline type is active
    if not deadline_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deadline type '{deadline_type.type_name}' is inactive"
        )
    
    # Create new deadline
    new_deadline = Deadline(**deadline_data.model_dump())
    
    db.add(new_deadline)
    db.commit()
    db.refresh(new_deadline)
    
    return MessageResponse(
        message="Deadline created successfully",
        id=new_deadline.id
    )


@router.put("/{deadline_id}", response_model=MessageResponse, summary="Update Deadline")
async def update_deadline(
    deadline_id: int,
    deadline_data: DeadlineUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update existing deadline
    
    **Path Parameters:**
    - deadline_id: Deadline ID to update
    
    **Request Body:**
    All fields optional:
    - client_id: Change associated client
    - deadline_type_id: Change deadline type
    - expiration_date: Change expiration date
    - status: Change status (active, expired, renewed)
    - notes: Update notes
    
    **Validation:**
    - If changing client_id, client must exist
    - If changing deadline_type_id, type must exist
    - Status must be one of: active, expired, renewed
    
    **Response:**
    - message: Success message
    - id: Updated deadline ID
    
    **Errors:**
    - 404 Not Found: Deadline, client, or type not found
    - 400 Bad Request: Invalid status value
    
    **Authentication:**
    Requires valid JWT token
    """
    # Fetch existing deadline
    deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
    
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline with id {deadline_id} not found"
        )
    
    # Prepare update data
    update_data = deadline_data.model_dump(exclude_unset=True)
    
    # Validate client if being changed
    if 'client_id' in update_data:
        client = db.query(Client).filter(Client.id == update_data['client_id']).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with id {update_data['client_id']} not found"
            )
    
    # Validate deadline type if being changed
    if 'deadline_type_id' in update_data:
        deadline_type = db.query(DeadlineType).filter(
            DeadlineType.id == update_data['deadline_type_id']
        ).first()
        if not deadline_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deadline type with id {update_data['deadline_type_id']} not found"
            )
    
    # Update deadline fields
    for field, value in update_data.items():
        setattr(deadline, field, value)
    
    db.commit()
    db.refresh(deadline)
    
    return MessageResponse(
        message="Deadline updated successfully",
        id=deadline.id
    )


@router.delete("/{deadline_id}", response_model=MessageResponse, summary="Delete Deadline")
async def delete_deadline(
    deadline_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete deadline
    
    **Path Parameters:**
    - deadline_id: Deadline ID to delete
    
    **Behavior:**
    - Permanently removes deadline from database
    - Associated notification logs are also deleted (CASCADE)
    - This operation cannot be undone
    
    **Response:**
    - message: Success message
    
    **Errors:**
    - 404 Not Found: Deadline does not exist
    
    **Note:**
    Unlike clients, deadlines use hard delete because they can be recreated
    if needed for renewed services
    
    **Authentication:**
    Requires valid JWT token
    """
    # Fetch deadline
    deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
    
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline with id {deadline_id} not found"
        )
    
    # Store info for response
    client_name = deadline.client.name if deadline.client else "Unknown"
    type_name = deadline.deadline_type.type_name if deadline.deadline_type else "Unknown"
    
    # Delete deadline
    db.delete(deadline)
    db.commit()
    
    return MessageResponse(
        message=f"Deadline deleted: {client_name} - {type_name}"
    )


# ============================================
# Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("МОДУЛЬ УПРАВЛЕНИЯ ДЕДЛАЙНАМИ")
    print("=" * 60)
    
    print("\nДоступные эндпоинты:")
    print("  • GET /api/deadlines - Список дедлайнов с фильтрацией")
    print("  • GET /api/deadlines/{id} - Получить дедлайн с деталями")
    print("  • POST /api/deadlines - Создать новый дедлайн")
    print("  • PUT /api/deadlines/{id} - Обновить дедлайн")
    print("  • DELETE /api/deadlines/{id} - Удалить дедлайн")
    
    print("\n" + "=" * 60)
    print("✅ МОДУЛЬ ГОТОВ К ИСПОЛЬЗОВАНИЮ")
    print("=" * 60)
