# -*- coding: utf-8 -*-
"""
API endpoints для управления пользователями (только для администраторов)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..dependencies import get_db
from ..models.user import WebUser
from ..models.schemas import UserCreate, UserUpdate, UserResponse, MessageResponse
from ..services.auth_service import get_password_hash, decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/users", tags=["Users"])
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


def check_admin_role(current_user: dict = Depends(get_current_user)):
    """Проверка прав администратора"""
    if current_user.get('role') != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может управлять пользователями"
        )
    return current_user


@router.get("", response_model=List[UserResponse])
async def get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role)
):
    """
    Получить список всех пользователей (только для администратора)
    """
    users = db.query(WebUser).order_by(WebUser.username).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role)
):
    """
    Получить пользователя по ID (только для администратора)
    """
    user = db.query(WebUser).filter(WebUser.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    
    return user


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role)
):
    """
    Создать нового пользователя (только для администратора)
    """
    # Проверка уникальности username
    existing_user = db.query(WebUser).filter(WebUser.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь с именем '{user_data.username}' уже существует"
        )
    
    # Проверка уникальности email
    if user_data.email:
        existing_email = db.query(WebUser).filter(WebUser.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Пользователь с email '{user_data.email}' уже существует"
            )
    
    # Создание нового пользователя
    new_user = WebUser(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=user_data.is_active,
        password_hash=get_password_hash(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return MessageResponse(
        message=f"Пользователь '{new_user.username}' успешно создан",
        id=new_user.id
    )


@router.put("/{user_id}", response_model=MessageResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role)
):
    """
    Обновить данные пользователя (только для администратора)
    """
    user = db.query(WebUser).filter(WebUser.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    
    # Обновление данных
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Проверка уникальности username при изменении
    if 'username' in update_data and update_data['username'] != user.username:
        existing = db.query(WebUser).filter(
            WebUser.username == update_data['username'],
            WebUser.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Пользователь с именем '{update_data['username']}' уже существует"
            )
    
    # Проверка уникальности email при изменении
    if 'email' in update_data and update_data['email'] != user.email:
        existing = db.query(WebUser).filter(
            WebUser.email == update_data['email'],
            WebUser.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Пользователь с email '{update_data['email']}' уже существует"
            )
    
    # Хеширование нового пароля если он передан
    if 'password' in update_data and update_data['password']:
        update_data['password_hash'] = get_password_hash(update_data['password'])
        del update_data['password']
    
    # Применение изменений
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return MessageResponse(
        message=f"Пользователь '{user.username}' успешно обновлён",
        id=user.id
    )


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role)
):
    """
    Деактивировать пользователя (только для администратора)
    """
    user = db.query(WebUser).filter(WebUser.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )
    
    # Запрет на деактивацию самого себя
    if user.id == int(current_user.get('sub', 0)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя деактивировать свою учётную запись"
        )
    
    # Мягкое удаление - деактивация
    user.is_active = False
    db.commit()
    
    return MessageResponse(
        message=f"Пользователь '{user.username}' деактивирован"
    )
