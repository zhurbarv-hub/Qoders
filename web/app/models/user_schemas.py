# -*- coding: utf-8 -*-
"""
Pydantic схемы для унифицированной модели пользователей (User)
Объединяет клиентов, менеджеров и администраторов
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime


# ============================================
# БАЗОВЫЕ СХЕМЫ ПОЛЬЗОВАТЕЛЕЙ
# ============================================

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr = Field(..., description="Email пользователя (уникальный)")
    full_name: str = Field(..., min_length=1, max_length=255, description="Полное имя")
    role: str = Field(..., pattern="^(client|manager|admin)$", description="Роль пользователя")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    address: Optional[str] = Field(None, description="Адрес")
    notes: Optional[str] = Field(None, description="Примечания")
    is_active: bool = Field(True, description="Активен ли пользователь")


class UserCreateByAdmin(UserBase):
    """Схема для создания пользователя администратором"""
    # Логин (обязательно при создании)
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$", description="Логин (латинские символы, цифры, подчеркивание)")
    
    # Для клиентов - обязательные поля
    inn: Optional[str] = Field(None, min_length=10, max_length=12, description="ИНН (только для клиентов)")
    company_name: Optional[str] = Field(None, max_length=255, description="Название компании (для клиентов)")
    
    # Telegram ID (для админов и менеджеров)
    telegram_id: Optional[str] = Field(None, max_length=50, description="Telegram ID (для админов и менеджеров)")
    
    # Настройки уведомлений (только для клиентов)
    notification_days: Optional[str] = Field("14,7,3", description="Дни до дедлайна для уведомлений")
    notifications_enabled: bool = Field(True, description="Включены ли уведомления")
    
    # Опциональный пароль (если не указан, отправляется приглашение по email)
    password: Optional[str] = Field(None, min_length=6, description="Пароль (опционально)")
    
    # Флаг отправки email приглашения
    send_invitation: bool = Field(True, description="Отправить email приглашение")
    
    @validator('inn')
    def validate_inn(cls, v, values):
        """Проверка ИНН для клиентов"""
        if v is not None:
            if not v.isdigit():
                raise ValueError('ИНН должен содержать только цифры')
            if len(v) not in [10, 12]:
                raise ValueError('ИНН должен быть длиной 10 или 12 цифр')
        elif values.get('role') == 'client':
            raise ValueError('ИНН обязателен для клиентов')
        return v
    
    @validator('company_name')
    def validate_company_name(cls, v, values):
        """Проверка названия компании для клиентов"""
        if values.get('role') == 'client' and not v:
            raise ValueError('Название компании обязательно для клиентов')
        return v
    
    @validator('telegram_id')
    def validate_telegram_id(cls, v, values):
        """Проверка обязательности Telegram ID для администраторов и менеджеров"""
        role = values.get('role')
        if role in ['admin', 'manager'] and not v:
            raise ValueError('Telegram ID обязателен для администраторов и менеджеров')
        return v


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, pattern="^(client|manager|admin)$", description="Роль пользователя")
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    
    # Для клиентов
    inn: Optional[str] = Field(None, min_length=10, max_length=12)
    company_name: Optional[str] = Field(None, max_length=255)
    notification_days: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    
    # Telegram (обновляется ботом)
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Пароль (для смены пароля администратором или самим пользователем)
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="Новый пароль")
    
    @validator('inn')
    def validate_inn(cls, v):
        """Проверка ИНН"""
        if v is not None:
            if not v.isdigit():
                raise ValueError('ИНН должен содержать только цифры')
            if len(v) not in [10, 12]:
                raise ValueError('ИНН должен быть длиной 10 или 12 цифр')
        return v


class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    
    # Контактная информация
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    
    # Для клиентов
    inn: Optional[str] = None
    company_name: Optional[str] = None
    
    # Telegram интеграция
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Настройки уведомлений
    notification_days: Optional[str] = None
    notifications_enabled: bool = True
    
    # Статус
    is_active: bool
    registered_at: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    last_login: Optional[datetime] = None  # Последний вход в систему
    created_at: datetime
    updated_at: datetime
    
    # Флаг - установлен ли пароль
    has_password: bool = False
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Схема списка пользователей с пагинацией"""
    total: int
    users: List[UserResponse]
    page: int
    page_size: int
    total_pages: int


# ============================================
# СХЕМЫ ДЛЯ АКТИВАЦИИ И УСТАНОВКИ ПАРОЛЯ
# ============================================

class ActivationTokenValidate(BaseModel):
    """Схема для валидации токена активации"""
    token: str = Field(..., min_length=10, description="Токен активации из email")


class ActivationTokenResponse(BaseModel):
    """Ответ валидации токена"""
    valid: bool
    email: Optional[str] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    message: str


class SetPasswordRequest(BaseModel):
    """Схема для установки пароля при активации"""
    token: str = Field(..., min_length=10, description="Токен активации")
    password: str = Field(..., min_length=6, max_length=100, description="Новый пароль")
    password_confirm: str = Field(..., min_length=6, max_length=100, description="Подтверждение пароля")
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        """Проверка совпадения паролей"""
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v


class PasswordResetRequest(BaseModel):
    """Схема запроса сброса пароля"""
    email: EmailStr = Field(..., description="Email пользователя")


class PasswordResetConfirm(BaseModel):
    """Схема подтверждения сброса пароля"""
    token: str = Field(..., min_length=10, description="Токен сброса пароля")
    new_password: str = Field(..., min_length=6, max_length=100, description="Новый пароль")
    password_confirm: str = Field(..., min_length=6, max_length=100, description="Подтверждение пароля")
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        """Проверка совпадения паролей"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Пароли не совпадают')
        return v


# ============================================
# СХЕМЫ ДЛЯ TELEGRAM ИНТЕГРАЦИИ
# ============================================

class TelegramRegistrationRequest(BaseModel):
    """Схема для регистрации через Telegram бот"""
    registration_code: str = Field(..., min_length=6, max_length=20, description="Код регистрации")
    telegram_id: str = Field(..., description="Telegram ID пользователя")
    telegram_username: Optional[str] = Field(None, description="Telegram username")
    first_name: Optional[str] = Field(None, description="Имя из Telegram")
    last_name: Optional[str] = Field(None, description="Фамилия из Telegram")


class TelegramRegistrationResponse(BaseModel):
    """Ответ на регистрацию через Telegram"""
    success: bool
    message: str
    user_id: Optional[int] = None
    email: Optional[str] = None
    company_name: Optional[str] = None


# ============================================
# СХЕМЫ ДЛЯ ПРИГЛАШЕНИЙ
# ============================================

class ResendInvitationRequest(BaseModel):
    """Схема для повторной отправки приглашения"""
    user_id: int = Field(..., gt=0, description="ID пользователя")
    regenerate_code: bool = Field(False, description="Регенерировать код регистрации для Telegram")


class InvitationResponse(BaseModel):
    """Ответ на отправку приглашения"""
    success: bool
    message: str
    activation_token: Optional[str] = None
    registration_code: Optional[str] = None
    code_expires_at: Optional[datetime] = None
