"""
Обработчики команд просмотра дедлайнов Telegram бота
"""
import logging
from datetime import date, timedelta
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from backend.models import Client, Deadline, DeadlineType
from bot.services.formatter import format_deadline_list

logger = logging.getLogger(__name__)

# Создаём роутер для команд дедлайнов
router = Router()


@router.message(Command('list'))
async def cmd_list(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    db_session: Session = None,
    **kwargs
):
    """
    Обработчик команды /list
    Показывает все дедлайны (30 дней вперёд)
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        client_id: ID клиента (для клиентов)
        db_session: Сессия базы данных
    """
    user = message.from_user
    logger.info(f"📋 /list от пользователя {user.id}, роль={user_role}")
    
    try:
        # Получаем дедлайны
        today = date.today()
        days_ahead = today + timedelta(days=30)
        
        query = db_session.query(Deadline).join(Client).join(DeadlineType).filter(
            Deadline.status == 'active',
            Deadline.expiration_date >= today,
            Deadline.expiration_date <= days_ahead
        )
        
        # Для клиентов фильтруем по их ID
        if user_role == 'client' and client_id:
            query = query.filter(Deadline.client_id == client_id)
        
        deadlines = query.order_by(Deadline.expiration_date.asc()).all()
        
        # Формируем список для форматтера
        deadline_list = []
        for d in deadlines:
            days_remaining = (d.expiration_date - today).days
            deadline_list.append({
                'client_name': d.client.name,
                'client_inn': d.client.inn,
                'deadline_type_name': d.deadline_type.type_name,
                'expiration_date': d.expiration_date,
                'days_remaining': days_remaining
            })
        
        # Форматируем и отправляем
        if deadline_list:
            title = "📋 Ваши дедлайны (30 дней)" if user_role == 'client' else "📋 Все дедлайны (30 дней)"
            response = format_deadline_list(deadline_list)
        else:
            response = "✅ Нет дедлайнов на ближайшие 30 дней"
        
        await message.answer(response, parse_mode='HTML')
        logger.info(f"✅ Отправлено {len(deadline_list)} дедлайнов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /list: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "⚠️ Произошла ошибка при получении списка дедлайнов",
            parse_mode='HTML'
        )


@router.message(Command('today'))
async def cmd_today(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    db_session: Session = None,
    **kwargs
):
    """
    Обработчик команды /today
    Показывает дедлайны на сегодня
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        client_id: ID клиента (для клиентов)
        db_session: Сессия базы данных
    """
    user = message.from_user
    logger.info(f"📅 /today от пользователя {user.id}, роль={user_role}")
    
    try:
        # Получаем дедлайны на сегодня
        today = date.today()
        
        query = db_session.query(Deadline).join(Client).join(DeadlineType).filter(
            Deadline.status == 'active',
            Deadline.expiration_date == today
        )
        
        # Для клиентов фильтруем по их ID
        if user_role == 'client' and client_id:
            query = query.filter(Deadline.client_id == client_id)
        
        deadlines = query.order_by(Deadline.expiration_date.asc()).all()
        
        # Формируем список
        deadline_list = []
        for d in deadlines:
            deadline_list.append({
                'client_name': d.client.name,
                'client_inn': d.client.inn,
                'deadline_type_name': d.deadline_type.type_name,
                'expiration_date': d.expiration_date,
                'days_remaining': 0
            })
        
        # Форматируем и отправляем
        if deadline_list:
            title = "📅 Дедлайны на сегодня"
            response = format_deadline_list(deadline_list)
        else:
            response = "🎉 На сегодня нет дедлайнов!"
        
        await message.answer(response, parse_mode='HTML')
        logger.info(f"✅ Отправлено {len(deadline_list)} дедлайнов на сегодня")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /today: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "⚠️ Произошла ошибка при получении дедлайнов на сегодня",
            parse_mode='HTML'
        )


@router.message(Command('week'))
async def cmd_week(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    db_session: Session = None,
    **kwargs
):
    """
    Обработчик команды /week
    Показывает дедлайны на неделю
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        client_id: ID клиента (для клиентов)
        db_session: Сессия базы данных
    """
    user = message.from_user
    logger.info(f"📆 /week от пользователя {user.id}, роль={user_role}")
    
    try:
        # Получаем дедлайны на неделю
        today = date.today()
        week_later = today + timedelta(days=7)
        
        query = db_session.query(Deadline).join(Client).join(DeadlineType).filter(
            Deadline.status == 'active',
            Deadline.expiration_date >= today,
            Deadline.expiration_date <= week_later
        )
        
        # Для клиентов фильтруем по их ID
        if user_role == 'client' and client_id:
            query = query.filter(Deadline.client_id == client_id)
        
        deadlines = query.order_by(Deadline.expiration_date.asc()).all()
        
        # Формируем список
        deadline_list = []
        for d in deadlines:
            days_remaining = (d.expiration_date - today).days
            deadline_list.append({
                'client_name': d.client.name,
                'client_inn': d.client.inn,
                'deadline_type_name': d.deadline_type.type_name,
                'expiration_date': d.expiration_date,
                'days_remaining': days_remaining
            })
        
        # Форматируем и отправляем
        if deadline_list:
            title = "📆 Дедлайны на неделю"
            response = format_deadline_list(deadline_list)
        else:
            response = "🎉 На этой неделе нет дедлайнов!"
        
        await message.answer(response, parse_mode='HTML')
        logger.info(f"✅ Отправлено {len(deadline_list)} дедлайнов на неделю")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /week: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "⚠️ Произошла ошибка при получении дедлайнов на неделю",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']