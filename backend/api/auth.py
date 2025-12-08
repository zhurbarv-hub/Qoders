"""
Authentication API Endpoints for KKT Services Expiration Management System

This module provides authentication endpoints:
- POST /api/auth/login - User login with email/password
- POST /api/auth/logout - User logout (client-side token deletion)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas import LoginRequest, Token, MessageResponse
from backend.utils.security import (
    verify_password,
    create_access_token,
    create_user_token_data,
    get_token_expiration_seconds
)
from backend.dependencies import get_current_user


# Create API router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, summary="User Login")
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and obtain JWT access token
    
    **Flow:**
    1. Receive email and password
    2. Query database for user by email
    3. Verify password hash matches
    4. Check user is_active status
    5. Generate JWT token
    6. Return token with expiration
    
    **Request Body:**
    - email: User email address
    - password: User password (minimum 8 characters)
    
    **Response:**
    - access_token: JWT token string
    - token_type: "bearer"
    - expires_in: Token validity in seconds
    
    **Errors:**
    - 400 Bad Request: Invalid email format or missing fields
    - 401 Unauthorized: Invalid credentials or inactive user
    """
    # Query user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    # Create token data
    token_data = create_user_token_data(
        user_id=user.id,
        email=user.email,
        role=user.role
    )
    
    # Generate JWT token
    access_token = create_access_token(data=token_data)
    
    # Return token response
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=get_token_expiration_seconds()
    )


@router.post("/logout", response_model=MessageResponse, summary="User Logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user (client-side token deletion)
    
    This endpoint confirms logout on server side. The actual logout is performed
    client-side by deleting the JWT token from localStorage.
    
    For enhanced security, a token blacklist can be implemented in the future.
    
    **Headers:**
    - Authorization: Bearer {access_token}
    
    **Response:**
    - message: Success message
    
    **Note:**
    Client must delete the access_token from localStorage after receiving response.
    """
    return MessageResponse(
        message=f"User {current_user.email} logged out successfully"
    )


@router.get("/me", response_model=dict, summary="Get Current User Info")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get information about currently authenticated user
    
    **Headers:**
    - Authorization: Bearer {access_token}
    
    **Response:**
    - id: User ID
    - email: User email
    - full_name: User full name
    - role: User role
    - is_active: Account status
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


# ============================================
# Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("МОДУЛЬ АУТЕНТИФИКАЦИИ")
    print("=" * 60)
    
    print("\nДоступные эндпоинты:")
    print("  • POST /api/auth/login - Вход в систему")
    print("  • POST /api/auth/logout - Выход из системы")
    print("  • GET /api/auth/me - Информация о текущем пользователе")
    
    print("\n" + "=" * 60)
    print("✅ МОДУЛЬ ГОТОВ К ИСПОЛЬЗОВАНИЮ")
    print("=" * 60)
