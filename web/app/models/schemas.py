# -*- coding: utf-8 -*-
"""
Pydantic схемы для валидации запросов и ответов
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Схема запроса на вход"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserInfo(BaseModel):
    """Информация о пользователе"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Ответ с токеном доступа"""
    access_token: str
    token_type: str = "bearer"
    user: UserInfo