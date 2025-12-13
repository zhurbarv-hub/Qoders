# -*- coding: utf-8 -*-
"""
API для управления кассовыми аппаратами
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

from ..models import CashRegister
from ..models.user import User
from ..dependencies import get_db
from ..services.auth_service import decode_token
from ..services.cash_register_deadline_service import CashRegisterDeadlineService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/cash-registers", tags=["Cash Registers"])
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


# Schemas
class CashRegisterCreate(BaseModel):
    user_id: int = Field(..., description="ID клиента")
    serial_number: str = Field(..., min_length=1, max_length=50, description="Заводской номер ККТ")
    fiscal_drive_number: str = Field(..., min_length=1, max_length=50, description="Номер фискального накопителя")
    register_name: str = Field(..., min_length=1, max_length=100, description="Название кассы")
    installation_address: Optional[str] = Field(None, max_length=500, description="Адрес установки")
    ofd_provider_id: Optional[int] = Field(None, description="ID провайдера ОФД")
    notes: Optional[str] = Field(None, description="Примечание")
    fn_replacement_date: Optional[date] = Field(None, description="Дата замены ФН")
    ofd_renewal_date: Optional[date] = Field(None, description="Дата продления ОФД")


class CashRegisterUpdate(BaseModel):
    serial_number: Optional[str] = Field(None, min_length=1, max_length=50)
    fiscal_drive_number: Optional[str] = Field(None, min_length=1, max_length=50)
    register_name: Optional[str] = Field(None, min_length=1, max_length=100)
    installation_address: Optional[str] = Field(None, max_length=500)
    ofd_provider_id: Optional[int] = Field(None)
    notes: Optional[str] = Field(None)
    fn_replacement_date: Optional[date] = Field(None)
    ofd_renewal_date: Optional[date] = Field(None)
    is_active: Optional[bool] = Field(None)


class CashRegisterResponse(BaseModel):
    id: int
    user_id: int
    serial_number: str
    fiscal_drive_number: str
    register_name: str
    installation_address: Optional[str] = None
    ofd_provider_id: Optional[int] = None
    notes: Optional[str] = None
    fn_replacement_date: Optional[date] = None
    ofd_renewal_date: Optional[date] = None
    is_active: bool

    class Config:
        from_attributes = True


# Endpoints
@router.get("", response_model=List[CashRegisterResponse])
async def list_cash_registers(
    user_id: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить список кассовых аппаратов"""
    query = db.query(CashRegister)
    
    if user_id:
        query = query.filter(CashRegister.user_id == user_id)
    
    query = query.filter(CashRegister.is_active == True)
    registers = query.all()
    
    return registers


@router.get("/{register_id}", response_model=CashRegisterResponse)
async def get_cash_register(
    register_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить кассовый аппарат по ID"""
    register = db.query(CashRegister).filter(CashRegister.id == register_id).first()
    
    if not register:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кассовый аппарат не найден"
        )
    
    return register


@router.post("", response_model=CashRegisterResponse, status_code=status.HTTP_201_CREATED)
async def create_cash_register(
    data: CashRegisterCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создать новый кассовый аппаратс автоматическим созданием дедлайнов"""
    try:
        # Проверка существования клиента
        user = db.query(User).filter(User.id == data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Клиент не найден"
            )
        
        # Проверка уникальности серийного номера
        existing = db.query(CashRegister).filter(
            CashRegister.serial_number == data.serial_number
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Кассовый аппарат с таким серийным номером уже существует"
            )
        
        # Создание кассы
        register = CashRegister(
            user_id=data.user_id,
            serial_number=data.serial_number,
            fiscal_drive_number=data.fiscal_drive_number,
            register_name=data.register_name,
            installation_address=data.installation_address,
            ofd_provider_id=data.ofd_provider_id,
            notes=data.notes,
            fn_replacement_date=data.fn_replacement_date,
            ofd_renewal_date=data.ofd_renewal_date
        )
        
        db.add(register)
        db.flush()  # Получить ID до commit
        
        # Автоматическое создание дедлайнов
        deadline_service = CashRegisterDeadlineService(db)
        deadline_service.sync_deadlines_on_create(
            cash_register_id=register.id,
            user_id=register.user_id,
            register_name=register.register_name,
            fn_replacement_date=data.fn_replacement_date,
            ofd_renewal_date=data.ofd_renewal_date
        )
        
        db.commit()
        db.refresh(register)
        
        return register
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании кассового аппарата: {str(e)}"
        )


@router.put("/{register_id}", response_model=CashRegisterResponse)
async def update_cash_register(
    register_id: int,
    data: CashRegisterUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить кассовый аппарат с автоматической синхронизацией дедлайнов"""
    try:
        register = db.query(CashRegister).filter(CashRegister.id == register_id).first()
        
        if not register:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Кассовый аппарат не найден"
            )
        
        # Проверка уникальности серийного номера при изменении
        if data.serial_number and data.serial_number != register.serial_number:
            existing = db.query(CashRegister).filter(
                CashRegister.serial_number == data.serial_number,
                CashRegister.id != register_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Кассовый аппарат с таким серийным номером уже существует"
                )
        
        # Сохранение старых значений дат для сравнения
        old_fn_date = register.fn_replacement_date
        old_ofd_date = register.ofd_renewal_date
        
        # Обновление полей
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(register, field, value)
        
        db.flush()  # Применить изменения до commit
        
        # Автоматическая синхронизация дедлайнов
        deadline_service = CashRegisterDeadlineService(db)
        deadline_service.sync_deadlines_on_update(
            cash_register_id=register.id,
            user_id=register.user_id,
            register_name=register.register_name,
            old_fn_date=old_fn_date,
            new_fn_date=register.fn_replacement_date,
            old_ofd_date=old_ofd_date,
            new_ofd_date=register.ofd_renewal_date
        )
        
        db.commit()
        db.refresh(register)
        
        return register
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении кассового аппарата: {str(e)}"
        )


@router.delete("/{register_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cash_register(
    register_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удалить (деактивировать) кассовый аппарат"""
    register = db.query(CashRegister).filter(CashRegister.id == register_id).first()
    
    if not register:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кассовый аппарат не найден"
        )
    
    # Мягкое удаление
    register.is_active = False
    db.commit()
    
    return None
