# -*- coding: utf-8 -*-
"""
Сервис аутентификации
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

# ОТНОСИТЕЛЬНЫЕ ИМПОРТЫ
from ..models.user import User
from ..config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Аутентификация пользователя
    
    Ищет пользователя по username или email в таблице users
    """
    # Попробуем найти по username
    user = db.query(User).filter(User.username == username).first()
    
    # Если не найден по username, попробуем по email
    if not user:
        user = db.query(User).filter(User.email == username).first()
    
    if not user:
        return None
    
    # Проверка наличия пароля
    if not user.password_hash:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    if not user.is_active:
        return None
    
    # Обновляем время последнего входа
    user.last_interaction = datetime.utcnow()
    db.commit()
    
    return user


def decode_token(token: str) -> Optional[dict]:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None