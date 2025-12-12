"""
Обработчики команд просмотра дедлайнов Telegram бота
ОБНОВЛЕНО: добавлена поддержка Web API и команда /next
"""
import logging
from datetime import date, timedelta
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from backend.models import User, Deadline, DeadlineType
from bot.services.formatter import format_deadline_list
from bot.services import checker

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
    ОБНОВЛЕНО: использует checker service с API интеграцией
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        client_id: ID клиента (для клиентов)
        db_session: Сессия базы данных
    """
    user = message.from_user
    logger.info(f"📋 /list от пользователя {user.id}, роль={user_role}")
    
    try:
        # Получаем дедлайны через checker service (использует API или fallback)
        deadlines = await checker.get_expiring_deadlines(days=30)
        
        # Для клиентов фильтруем по их ID
        if user_role == 'client' and client_id:
            deadlines = [d for d in deadlines if d.get('client_id') == client_id]
        
        # Форматируем и отправляем
        if deadlines:
            title = "📋 Ваши дедлайны (30 дней)" if user_role == 'client' else "📋 Все дедлайны (30 дней)"
            response = format_deadline_list(deadlines, title=title)
        else:
            response = "✅ Нет дедлайнов на ближайшие 30 дней"
        
        await message.answer(response, parse_mode='HTML')
        logger.info(f"✅ Отправлено {len(deadlines)} дедлайнов")
        
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
    ОБНОВЛЕНО: использует checker service с API интеграцией
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        client_id: ID клиента (для клиентов)
        db_session: Сессия базы данных
    """
    user = message.from_user
    logger.info(f"📅 /today от пользователя {user.id}, роль={user_role}")
    
    try:
        # Получаем все дедлайны на ближайшие дни
        all_deadlines = await checker.get_expiring_deadlines(days=1)
        
        # Фильтруем только сегодняшние
        today = date.today()
        deadlines = [
            d for d in all_deadlines 
            if d.get('days_remaining') == 0
        ]
        
        # Для клиентов фильтруем по их ID
        if user_role == 'client' and client_id:
            deadlines = [d for d in deadlines if d.get('client_id') == client_id]
        
        # Форматируем и отправляем
        if deadlines:
            response = format_deadline_list(deadlines, title="📅 Дедлайны на сегодня")
        else:
            response = "🎉 На сегодня нет дедлайнов!"
        
        await message.answer(response, parse_mode='HTML')
        logger.info(f"✅ Отправлено {len(deadlines)} дедлайнов на сегодня")
        
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
    ОБНОВЛЕНО: использует checker service с API интеграцией
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        client_id: ID клиента (для клиентов)
        db_session: Сессия базы данных
    """
    user = message.from_user
    logger.info(f"📆 /week от пользователя {user.id}, роль={user_role}")
    
    try:
        # Получаем дедлайны на 7 дней через checker service
        deadlines = await checker.get_expiring_deadlines(days=7)
        
        # Для клиентов фильтруем по их ID
        if user_role == 'client' and client_id:
            deadlines = [d for d in deadlines if d.get('client_id') == client_id]
        
        # Форматируем и отправляем
        if deadlines:
            response = format_deadline_list(deadlines, title="📆 Дедлайны на неделю")
        else:
            response = "🎉 На этой неделе нет дедлайнов!"
        
        await message.answer(response, parse_mode='HTML')
        logger.info(f"✅ Отправлено {len(deadlines)} дедлайнов на неделю")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /week: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "⚠️ Произошла ошибка при получении дедлайнов на неделю",
            parse_mode='HTML'
        )


@router.message(Command('next'))
async def cmd_next(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    db_session: Session = None,
    **kwargs
):
    """
    НОВАЯ КОМАНДА: /next <days>
    Показывает дедлайны на произвольное количество дней вперёд
    
    Примеры:
        /next 14 - дедлайны на 14 дней
        /next 30 - дедлайны на месяц
        /next - по умолчанию 14 дней
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        client_id: ID клиента (для клиентов)
        db_session: Сессия базы данных
    """
    user = message.from_user
    logger.info(f"🔮 /next от пользователя {user.id}, роль={user_role}")
    
    try:
        # Парсим количество дней из команды
        args = message.text.split()
        days = 14  # По умолчанию 14 дней
        
        if len(args) > 1:
            try:
                days = int(args[1])
                # Валидация: от 1 до 90 дней
                if days < 1 or days > 90:
                    await message.answer(
                        "⚠️ <b>Неверный параметр</b>\n\n"
                        "Укажите количество дней от 1 до 90.\n"
                        "Пример: <code>/next 14</code>",
                        parse_mode='HTML'
                    )
                    return
            except ValueError:
                await message.answer(
                    "⚠️ <b>Неверный формат</b>\n\n"
                    "Укажите число дней.\n"
                    "Пример: <code>/next 14</code>",
                    parse_mode='HTML'
                )
                return
        
        # Получаем дедлайны через checker service
        deadlines = await checker.get_expiring_deadlines(days=days)
        
        # Для клиентов фильтруем по их ID
        if user_role == 'client' and client_id:
            deadlines = [d for d in deadlines if d.get('client_id') == client_id]
        
        # Форматируем и отправляем
        if deadlines:
            title = f"🔮 Дедлайны на {days} дней"
            response = format_deadline_list(deadlines, title=title)
        else:
            response = f"✅ Нет дедлайнов на ближайшие {days} дней"
        
        await message.answer(response, parse_mode='HTML')
        logger.info(f"✅ Отправлено {len(deadlines)} дедлайнов на {days} дней")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /next: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "⚠️ Произошла ошибка при получении дедлайнов",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']