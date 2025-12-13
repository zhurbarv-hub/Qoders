# -*- coding: utf-8 -*-
"""
Сервис автоматического управления дедлайнами для кассовых аппаратов

Этот сервис обеспечивает автоматическое создание, обновление и отмену дедлайнов
при работе с полями fn_replacement_date и ofd_renewal_date в кассовых аппаратах.
"""
from datetime import date, datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
import logging

from ..models.client import Deadline, DeadlineType

logger = logging.getLogger(__name__)


class CashRegisterDeadlineService:
    """Сервис управления автоматическими дедлайнами для кассовых аппаратов"""
    
    # Названия типов дедлайнов
    FN_REPLACEMENT_TYPE = "Замена ФН"
    OFD_RENEWAL_TYPE = "Продление договора ОФД"  # Точное название из БД
    
    def __init__(self, db: Session):
        """
        Инициализация сервиса
        
        Args:
            db: Сессия SQLAlchemy для работы с БД
        """
        self.db = db
        self._fn_type_id: Optional[int] = None
        self._ofd_type_id: Optional[int] = None
    
    def get_deadline_type_id(self, type_name: str) -> Optional[int]:
        """
        Получить ID типа дедлайна по названию
        
        Args:
            type_name: Название типа дедлайна
            
        Returns:
            ID типа или None, если не найден
        """
        deadline_type = self.db.query(DeadlineType).filter(
            DeadlineType.type_name == type_name,
            DeadlineType.is_active == True
        ).first()
        
        if not deadline_type:
            logger.warning(f"Тип дедлайна '{type_name}' не найден в БД")
            return None
        
        return deadline_type.id
    
    @property
    def fn_type_id(self) -> Optional[int]:
        """Получить ID типа 'Замена ФН' (с кешированием)"""
        if self._fn_type_id is None:
            self._fn_type_id = self.get_deadline_type_id(self.FN_REPLACEMENT_TYPE)
        return self._fn_type_id
    
    @property
    def ofd_type_id(self) -> Optional[int]:
        """Получить ID типа 'Продление договора' (с кешированием)"""
        if self._ofd_type_id is None:
            self._ofd_type_id = self.get_deadline_type_id(self.OFD_RENEWAL_TYPE)
        return self._ofd_type_id
    
    def find_existing_deadline(
        self, 
        cash_register_id: int, 
        deadline_type_id: int
    ) -> Optional[Deadline]:
        """
        Найти существующий активный дедлайн для кассы и типа
        
        Args:
            cash_register_id: ID кассового аппарата
            deadline_type_id: ID типа дедлайна
            
        Returns:
            Найденный дедлайн или None
        """
        return self.db.query(Deadline).filter(
            Deadline.cash_register_id == cash_register_id,
            Deadline.deadline_type_id == deadline_type_id,
            Deadline.status == 'active'
        ).first()
    
    def create_deadline_for_register(
        self,
        cash_register_id: int,
        user_id: int,
        deadline_type_id: int,
        expiration_date: date,
        register_name: str,
        type_name: str
    ) -> Deadline:
        """
        Создать новый дедлайн для кассового аппарата
        
        Args:
            cash_register_id: ID кассового аппарата
            user_id: ID пользователя (владельца)
            deadline_type_id: ID типа дедлайна
            expiration_date: Дата истечения
            register_name: Название кассы
            type_name: Название типа дедлайна
            
        Returns:
            Созданный дедлайн
        """
        notes = f"Автоматически создано из карточки ККТ '{register_name}' ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        
        deadline = Deadline(
            user_id=user_id,
            cash_register_id=cash_register_id,
            deadline_type_id=deadline_type_id,
            expiration_date=expiration_date,
            status='active',
            notes=notes
        )
        
        self.db.add(deadline)
        logger.info(
            f"Создан дедлайн '{type_name}' для кассы ID={cash_register_id}, "
            f"дата: {expiration_date}"
        )
        
        return deadline
    
    def update_deadline_for_register(
        self,
        deadline: Deadline,
        new_expiration_date: date,
        type_name: str
    ) -> Deadline:
        """
        Обновить существующий дедлайн
        
        Args:
            deadline: Существующий дедлайн
            new_expiration_date: Новая дата истечения
            type_name: Название типа дедлайна
            
        Returns:
            Обновленный дедлайн
        """
        old_date = deadline.expiration_date
        deadline.expiration_date = new_expiration_date
        
        # Обновление notes с информацией об изменении
        update_note = f"\nОбновлено: {old_date} → {new_expiration_date} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        if deadline.notes:
            deadline.notes += update_note
        else:
            deadline.notes = f"Автоматически обновлено{update_note}"
        
        logger.info(
            f"Обновлен дедлайн '{type_name}' ID={deadline.id}: "
            f"{old_date} → {new_expiration_date}"
        )
        
        return deadline
    
    def cancel_deadline_for_register(
        self,
        deadline: Deadline,
        type_name: str
    ) -> Deadline:
        """
        Отменить дедлайн (изменить статус на 'cancelled')
        
        Args:
            deadline: Существующий дедлайн
            type_name: Название типа дедлайна
            
        Returns:
            Отмененный дедлайн
        """
        deadline.status = 'cancelled'
        
        # Добавление информации об отмене
        cancel_note = f"\nОтменено: дата удалена из карточки ККТ ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        if deadline.notes:
            deadline.notes += cancel_note
        else:
            deadline.notes = cancel_note
        
        logger.info(f"Отменен дедлайн '{type_name}' ID={deadline.id}")
        
        return deadline
    
    def sync_deadlines_on_create(
        self,
        cash_register_id: int,
        user_id: int,
        register_name: str,
        fn_replacement_date: Optional[date],
        ofd_renewal_date: Optional[date]
    ) -> Tuple[Optional[Deadline], Optional[Deadline]]:
        """
        Синхронизация дедлайнов при создании кассового аппарата
        
        Args:
            cash_register_id: ID кассового аппарата
            user_id: ID пользователя (владельца)
            register_name: Название кассы
            fn_replacement_date: Дата замены ФН (может быть None)
            ofd_renewal_date: Дата продления ОФД (может быть None)
            
        Returns:
            Tuple из (fn_deadline, ofd_deadline), каждый может быть None
        """
        fn_deadline = None
        ofd_deadline = None
        
        # Создание дедлайна для замены ФН
        if fn_replacement_date and self.fn_type_id:
            fn_deadline = self.create_deadline_for_register(
                cash_register_id=cash_register_id,
                user_id=user_id,
                deadline_type_id=self.fn_type_id,
                expiration_date=fn_replacement_date,
                register_name=register_name,
                type_name=self.FN_REPLACEMENT_TYPE
            )
        elif fn_replacement_date and not self.fn_type_id:
            logger.error(f"Не найден тип дедлайна '{self.FN_REPLACEMENT_TYPE}'")
        
        # Создание дедлайна для продления ОФД
        if ofd_renewal_date and self.ofd_type_id:
            ofd_deadline = self.create_deadline_for_register(
                cash_register_id=cash_register_id,
                user_id=user_id,
                deadline_type_id=self.ofd_type_id,
                expiration_date=ofd_renewal_date,
                register_name=register_name,
                type_name=self.OFD_RENEWAL_TYPE
            )
        elif ofd_renewal_date and not self.ofd_type_id:
            logger.error(f"Не найден тип дедлайна '{self.OFD_RENEWAL_TYPE}'")
        
        return fn_deadline, ofd_deadline
    
    def sync_deadlines_on_update(
        self,
        cash_register_id: int,
        user_id: int,
        register_name: str,
        old_fn_date: Optional[date],
        new_fn_date: Optional[date],
        old_ofd_date: Optional[date],
        new_ofd_date: Optional[date]
    ) -> Tuple[Optional[Deadline], Optional[Deadline]]:
        """
        Синхронизация дедлайнов при обновлении кассового аппарата
        
        Args:
            cash_register_id: ID кассового аппарата
            user_id: ID пользователя (владельца)
            register_name: Название кассы
            old_fn_date: Старая дата замены ФН
            new_fn_date: Новая дата замены ФН
            old_ofd_date: Старая дата продления ОФД
            new_ofd_date: Новая дата продления ОФД
            
        Returns:
            Tuple из (fn_deadline, ofd_deadline), каждый может быть None
        """
        fn_deadline = None
        ofd_deadline = None
        
        # Обработка изменений для замены ФН
        if old_fn_date != new_fn_date:
            if self.fn_type_id:
                existing_fn = self.find_existing_deadline(cash_register_id, self.fn_type_id)
                
                if new_fn_date is None:
                    # Удаление даты -> отмена дедлайна
                    if existing_fn:
                        fn_deadline = self.cancel_deadline_for_register(
                            existing_fn, self.FN_REPLACEMENT_TYPE
                        )
                elif existing_fn:
                    # Обновление существующего дедлайна
                    fn_deadline = self.update_deadline_for_register(
                        existing_fn, new_fn_date, self.FN_REPLACEMENT_TYPE
                    )
                else:
                    # Создание нового дедлайна
                    fn_deadline = self.create_deadline_for_register(
                        cash_register_id=cash_register_id,
                        user_id=user_id,
                        deadline_type_id=self.fn_type_id,
                        expiration_date=new_fn_date,
                        register_name=register_name,
                        type_name=self.FN_REPLACEMENT_TYPE
                    )
        
        # Обработка изменений для продления ОФД
        if old_ofd_date != new_ofd_date:
            if self.ofd_type_id:
                existing_ofd = self.find_existing_deadline(cash_register_id, self.ofd_type_id)
                
                if new_ofd_date is None:
                    # Удаление даты -> отмена дедлайна
                    if existing_ofd:
                        ofd_deadline = self.cancel_deadline_for_register(
                            existing_ofd, self.OFD_RENEWAL_TYPE
                        )
                elif existing_ofd:
                    # Обновление существующего дедлайна
                    ofd_deadline = self.update_deadline_for_register(
                        existing_ofd, new_ofd_date, self.OFD_RENEWAL_TYPE
                    )
                else:
                    # Создание нового дедлайна
                    ofd_deadline = self.create_deadline_for_register(
                        cash_register_id=cash_register_id,
                        user_id=user_id,
                        deadline_type_id=self.ofd_type_id,
                        expiration_date=new_ofd_date,
                        register_name=register_name,
                        type_name=self.OFD_RENEWAL_TYPE
                    )
        
        return fn_deadline, ofd_deadline
