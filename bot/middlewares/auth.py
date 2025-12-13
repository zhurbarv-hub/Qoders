# -*- coding: utf-8 -*-
"""
Аутентификационное middleware для Telegram бота
Проверяет права доступа пользователей и определяет их роль
"""

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Dict, Callable, Awaitable, List
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """
    Middleware для аутентификации пользователей Telegram бота
    """

    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка входящего события и проверка аутентификации
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Входящее событие (сообщение)
            data: Данные события
            
        Returns:
            Any: Результат выполнения обработчика
        """
        # Создаём сессию БД для обработчика
        db_session: Session = SessionLocal()
        
        try:
            # Получаем Telegram ID пользователя
            if isinstance(event, Message):
                user_id = event.from_user.id
                username = event.from_user.username or event.from_user.first_name
            elif isinstance(event, CallbackQuery):
                user_id = event.from_user.id
                username = event.from_user.username or event.from_user.first_name
            else:
                logger.warning(f"Неизвестный тип события: {type(event)}")
                return await handler(event, data)
            
            # Проверяем роль пользователя
            user_role, client_id = self._check_user_role(user_id)
            
            # Добавляем информацию о пользователе в данные события
            data['user_id'] = user_id
            data['username'] = username
            data['user_role'] = user_role
            data['client_id'] = client_id
            data['db_session'] = db_session  # ← ДОБАВИЛИ СЕССИЮ БД!
            
            logger.debug(f"Пользователь {user_id} ({username}) авторизован как {user_role}")
            
            # Передаем управление следующему обработчику
            return await handler(event, data)
            
        except Exception as e:
            logger.error(f"Ошибка аутентификации: {e}")
            # В случае ошибки продолжаем обработку без аутентификации
            data['user_role'] = 'unknown'
            data['client_id'] = None
            data['db_session'] = db_session  # ← И ЗДЕСЬ ТОЖЕ!
            return await handler(event, data)
            
        finally:
            # Закрываем сессию после обработки
            db_session.close()

    def _check_user_role(self, telegram_id: int) -> tuple:
        """
        Проверка роли пользователя по Telegram ID
        
        Args:
            telegram_id (int): Telegram ID пользователя
            
        Returns:
            tuple: (роль пользователя, ID клиента если клиент)
        """
        try:
            # Получаем конфигурацию бота
            from bot.config import get_bot_config
            config = get_bot_config()
            
            # 1. Проверяем, является ли пользователь администратором
            if telegram_id in config['telegram_admin_ids']:
                logger.info(f"✅ Пользователь {telegram_id} является администратором")
                return ('admin', None)
            
            # 2. Проверяем, является ли пользователь менеджером
            from backend.config import settings
            if telegram_id in settings.telegram_manager_ids_list:
                logger.info(f"✅ Пользователь {telegram_id} является менеджером")
                return ('manager', None)
            
            # 3. Проверяем, является ли пользователь зарегистрированным клиентом
            db: Session = SessionLocal()
            try:
                # Ищем пользователя в таблице users с ролью client
                user = db.query(models.User).filter(
                    models.User.telegram_id == str(telegram_id),
                    models.User.role == 'client',
                    models.User.is_active == True
                ).first()
                
                if user:
                    logger.debug(f"Пользователь {telegram_id} является клиентом ID={user.id} ({user.company_name})")
                    return ('client', user.id)
                else:
                    logger.debug(f"Пользователь {telegram_id} не найден в базе")
                    return ('unknown', None)
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Ошибка проверки роли пользователя {telegram_id}: {e}")
            return ('unknown', None)


def is_admin(user_id: int, admin_ids: List[int]) -> bool:
    """
    Проверка, является ли пользователь администратором
    
    Args:
        user_id (int): Telegram ID пользователя
        admin_ids (List[int]): Список Telegram ID администраторов
        
    Returns:
        bool: True если пользователь является администратором
    """
    return user_id in admin_ids


def get_client_by_telegram_id(telegram_id: int) -> dict:
    """
    Получение информации о клиенте по Telegram ID
    
    Args:
        telegram_id (int): Telegram ID пользователя
        
    Returns:
        dict: Информация о клиенте или None
    """
    try:
        db: Session = SessionLocal()
        try:
            # Ищем контакт и связанного клиента
            contact = db.query(models.Contact).join(models.Client).filter(
                models.Contact.telegram_id == str(telegram_id),
                models.Contact.notifications_enabled == True
            ).first()
            
            if contact and contact.client:
                return {
                    'client_id': contact.client.id,
                    'client_name': contact.client.name,
                    'client_inn': contact.client.inn,
                    'contact_id': contact.id
                }
            else:
                return None
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Ошибка получения клиента по Telegram ID {telegram_id}: {e}")
        return None


if __name__ == "__main__":
    # Тестирование middleware
    print("=" * 50)
    print("ТЕСТ АУТЕНТИФИКАЦИОННОГО MIDDLEWARE")
    print("=" * 50)
    
    print("Middleware готово к использованию")
    print("Для тестирования необходимо запустить бота")
    
    print("=" * 50)
    print("✅ Middleware готово к работе")
    print("=" * 50)