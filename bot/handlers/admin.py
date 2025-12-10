"""
Административные команды Telegram бота
Доступны только администратору
"""
import logging
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from bot.services.notifier import process_deadline_notifications
from bot.services.formatter import format_statistics
from backend.config import settings

logger = logging.getLogger(__name__)

# Создаём роутер для административных команд
router = Router()


@router.message(Command('check'))
async def cmd_check(
    message: Message,
    bot: Bot,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    Обработчик команды /check
    Принудительная проверка дедлайнов и отправка уведомлений
    
    Args:
        message: Сообщение от пользователя
        bot: Экземпляр бота
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
    # Проверка прав администратора
    if not is_admin:
        logger.warning(f"⛔ Попытка /check от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"🔍 /check от администратора {user.id}")
    
    # Отправляем сообщение о начале проверки
    status_msg = await message.answer(
        "🔄 <b>Запуск проверки дедлайнов...</b>\n\n"
        "Это может занять несколько секунд.",
        parse_mode='HTML'
    )
    
    try:
        # Получаем дни для проверки из конфигурации
        days_list = settings.notification_days_list
        
        total_stats = {
            'checked': 0,
            'sent': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Проверяем для каждого периода
        for days in days_list:
            logger.info(f"📅 Проверка дедлайнов за {days} дней")
            
            stats = await process_deadline_notifications(
                bot=bot,
                days=days
            )
            
            # Суммируем статистику
            total_stats['checked'] += stats.get('total_deadlines', 0)
            total_stats['sent'] += stats['sent']
            total_stats['failed'] += stats['failed']
            total_stats['skipped'] += stats['skipped']
        
        # Формируем отчёт
        report = f"""
✅ <b>Проверка завершена</b>

📊 <b>Результаты:</b>
• Проверено дедлайнов: <b>{total_stats['checked']}</b>
• Отправлено уведомлений: <b>{total_stats['sent']}</b>
• Пропущено (дубликаты): <b>{total_stats['skipped']}</b>
• Ошибок отправки: <b>{total_stats['failed']}</b>

⏰ Автоматическая проверка: <b>{settings.notification_check_time}</b> ({settings.notification_timezone})
📅 Дни уведомлений: <b>{', '.join(map(str, days_list))}</b>
""".strip()
        
        await status_msg.edit_text(report, parse_mode='HTML')
        logger.info(f"✅ Проверка завершена: {total_stats}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении /check: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при проверке</b>\n\n"
            f"<code>{str(e)[:200]}</code>\n\n"
            f"Проверьте логи для подробностей.",
            parse_mode='HTML'
        )


@router.message(Command('status'))
async def cmd_status(
    message: Message,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    Обработчик команды /status
    Показывает статистику системы
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
    # Проверка прав администратора
    if not is_admin:
        logger.warning(f"⛔ Попытка /status от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"📊 /status от администратора {user.id}")
    
    try:
        from backend.models import Client, Deadline, Contact
        from datetime import date, timedelta
        
        # Собираем статистику
        stats = {}
        
        # Количество активных клиентов
        stats['active_clients_count'] = db_session.query(Client).filter(
            Client.is_active == True
        ).count()
        
        # Количество дедлайнов по статусам
        all_deadlines = db_session.query(Deadline).filter(
            Deadline.status == 'active'
        ).all()
        
        stats['total_deadlines_count'] = len(all_deadlines)
        
        # Подсчёт по цветам
        today = date.today()
        green_count = 0
        yellow_count = 0
        red_count = 0
        expired_count = 0
        
        for deadline in all_deadlines:
            days_remaining = (deadline.expiration_date - today).days
            
            if days_remaining < 0:
                expired_count += 1
            elif days_remaining < 7:
                red_count += 1
            elif days_remaining < 14:
                yellow_count += 1
            else:
                green_count += 1
        
        stats['green_count'] = green_count
        stats['yellow_count'] = yellow_count
        stats['red_count'] = red_count
        stats['expired_count'] = expired_count
        
        # Ближайшие дедлайны
        upcoming = db_session.query(Deadline).join(
            Client
        ).filter(
            Deadline.status == 'active',
            Deadline.expiration_date >= today
        ).order_by(
            Deadline.expiration_date.asc()
        ).limit(5).all()
        
        stats['upcoming_deadlines'] = [
            {
                'client_name': d.client.name,
                'type_name': d.deadline_type.type_name,
                'expiration_date': d.expiration_date
            }
            for d in upcoming
        ]
        
        # Форматируем статистику
        status_text = format_statistics(stats)
        
        await message.answer(status_text, parse_mode='HTML')
        logger.info(f"✅ Статистика отправлена")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /status: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await message.answer(
            f"❌ <b>Ошибка при получении статистики</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']