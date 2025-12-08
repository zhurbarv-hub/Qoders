"""
Deadline Types API Endpoints for KKT Services Expiration Management System

This module provides endpoints for deadline type management:
- GET /api/deadline-types - List all deadline types
- GET /api/deadline-types/{id} - Get single deadline type
- POST /api/deadline-types - Create custom deadline type (admin only)
- PUT /api/deadline-types/{id} - Update deadline type (admin only)
- DELETE /api/deadline-types/{id} - Deactivate deadline type (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import DeadlineType, Deadline, User
from backend.schemas import (
    DeadlineTypeCreate,
    DeadlineTypeResponse,
    MessageResponse
)
from backend.dependencies import get_current_active_user, get_current_admin_user


# Create API router
router = APIRouter(prefix="/api/deadline-types", tags=["Deadline Types"])


@router.get("", response_model=List[DeadlineTypeResponse], summary="List Deadline Types")
async def list_deadline_types(
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all deadline types
    
    **Query Parameters:**
    - active_only: Show only active types (default: true)
    
    **Response:**
    - Array of deadline type objects sorted alphabetically
    
    **Types Include:**
    - System types (is_system=True): OFD, KKT Registration, etc.
    - Custom types (is_system=False): User-defined types
    
    **Authentication:**
    Requires valid JWT token
    """
    query = db.query(DeadlineType)
    
    if active_only:
        query = query.filter(DeadlineType.is_active == True)
    
    types = query.order_by(DeadlineType.type_name).all()
    
    return [DeadlineTypeResponse.model_validate(t) for t in types]


@router.get("/{type_id}", response_model=DeadlineTypeResponse, summary="Get Deadline Type")
async def get_deadline_type(
    type_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve single deadline type by ID
    
    **Path Parameters:**
    - type_id: Deadline type ID
    
    **Response:**
    - Deadline type object
    
    **Errors:**
    - 404 Not Found: Type does not exist
    
    **Authentication:**
    Requires valid JWT token
    """
    deadline_type = db.query(DeadlineType).filter(DeadlineType.id == type_id).first()
    
    if not deadline_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline type with id {type_id} not found"
        )
    
    return DeadlineTypeResponse.model_validate(deadline_type)


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, summary="Create Deadline Type")
async def create_deadline_type(
    type_data: DeadlineTypeCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new custom deadline type (admin only)
    
    **Request Body:**
    - type_name: Service type name (required, unique)
    - description: Type description (optional)
    
    **Response:**
    - message: Success message
    - id: New type ID
    
    **Errors:**
    - 409 Conflict: Type name already exists
    - 403 Forbidden: Non-admin user
    
    **Authentication:**
    Requires admin role
    """
    # Check for duplicate type name
    existing = db.query(DeadlineType).filter(
        DeadlineType.type_name == type_data.type_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Deadline type '{type_data.type_name}' already exists"
        )
    
    # Create new type (custom type, not system)
    new_type = DeadlineType(
        **type_data.model_dump(),
        is_system=False
    )
    
    db.add(new_type)
    db.commit()
    db.refresh(new_type)
    
    return MessageResponse(
        message=f"Deadline type '{new_type.type_name}' created successfully",
        id=new_type.id
    )


@router.put("/{type_id}", response_model=MessageResponse, summary="Update Deadline Type")
async def update_deadline_type(
    type_id: int,
    type_data: DeadlineTypeCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update deadline type (admin only)
    
    **Path Parameters:**
    - type_id: Type ID to update
    
    **Request Body:**
    - type_name: New type name (must be unique)
    - description: New description
    
    **Response:**
    - message: Success message
    - id: Updated type ID
    
    **Errors:**
    - 404 Not Found: Type does not exist
    - 409 Conflict: Type name already exists
    - 400 Bad Request: Cannot modify system types
    
    **Authentication:**
    Requires admin role
    """
    deadline_type = db.query(DeadlineType).filter(DeadlineType.id == type_id).first()
    
    if not deadline_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline type with id {type_id} not found"
        )
    
    # Prevent modification of system types
    if deadline_type.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify system deadline types"
        )
    
    # Check for duplicate name if being changed
    if type_data.type_name != deadline_type.type_name:
        existing = db.query(DeadlineType).filter(
            DeadlineType.type_name == type_data.type_name,
            DeadlineType.id != type_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Deadline type '{type_data.type_name}' already exists"
            )
    
    # Update fields
    deadline_type.type_name = type_data.type_name
    deadline_type.description = type_data.description
    
    db.commit()
    
    return MessageResponse(
        message=f"Deadline type updated successfully",
        id=deadline_type.id
    )


@router.delete("/{type_id}", response_model=MessageResponse, summary="Deactivate Deadline Type")
async def delete_deadline_type(
    type_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate deadline type (soft delete, admin only)
    
    **Path Parameters:**
    - type_id: Type ID to deactivate
    
    **Behavior:**
    - Sets is_active = False
    - Existing deadlines using this type remain unchanged
    - Type cannot be selected for new deadlines
    
    **Response:**
    - message: Success message
    
    **Errors:**
    - 404 Not Found: Type does not exist
    - 400 Bad Request: Cannot delete system types
    
    **Note:**
    System types cannot be deleted or deactivated
    
    **Authentication:**
    Requires admin role
    """
    deadline_type = db.query(DeadlineType).filter(DeadlineType.id == type_id).first()
    
    if not deadline_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deadline type with id {type_id} not found"
        )
    
    # Prevent deletion of system types
    if deadline_type.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system deadline types"
        )
    
    # Soft delete
    deadline_type.is_active = False
    
    db.commit()
    
    return MessageResponse(
        message=f"Deadline type '{deadline_type.type_name}' deactivated successfully"
    )


# ============================================
# Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("МОДУЛЬ ТИПОВ ДЕДЛАЙНОВ")
    print("=" * 60)
    
    print("\nДоступные эндпоинты:")
    print("  • GET /api/deadline-types - Список типов")
    print("  • GET /api/deadline-types/{id} - Получить тип")
    print("  • POST /api/deadline-types - Создать тип (admin)")
    print("  • PUT /api/deadline-types/{id} - Обновить тип (admin)")
    print("  • DELETE /api/deadline-types/{id} - Деактивировать тип (admin)")
    
    print("\n" + "=" * 60)
    print("✅ МОДУЛЬ ГОТОВ К ИСПОЛЬЗОВАНИЮ")
    print("=" * 60)
