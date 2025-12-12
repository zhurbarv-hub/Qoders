"""
Административные команды Telegram бота
Доступны только администратору
ОБНОВЛЕНО: добавлена команда /health, /status использует Web API
"""
import logging
import time
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from bot.services.notifier import process_deadline_notifications
from bot.services.formatter import format_api_statistics, format_health_status
from bot.services import checker
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
        
        # Определяем источник данных
        api_client = checker._api_client
        data_source = "🔌 Web API" if api_client else "💾 База данных"
        
        # Формируем отчёт
        report = f"""
✅ <b>Проверка завершена</b>

📊 <b>Результаты:</b>
• Проверено дедлайнов: <b>{total_stats['checked']}</b>
• Отправлено уведомлений: <b>{total_stats['sent']}</b>
• Пропущено (дубликаты): <b>{total_stats['skipped']}</b>
• Ошибок отправки: <b>{total_stats['failed']}</b>

📡 <b>Источник данных:</b> {data_source}

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
    ОБНОВЛЕНО: использует Web API для получения статистики
    
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
    
    # Показываем индикатор загрузки
    status_msg = await message.answer("⏳ Загрузка статистики...", parse_mode='HTML')
    
    try:
        # Получаем API клиент из checker service
        api_client = checker._api_client
        
        if api_client:
            # Попытка получить статистику через Web API
            try:
                start_time = time.time()
                stats = await api_client.get_dashboard_stats()
                response_time = int((time.time() - start_time) * 1000)  # в миллисекундах
                
                # Добавляем время ответа API
                stats['api_response_time'] = response_time
                stats['data_source'] = 'api'
                
                # Форматируем статистику из API
                status_text = format_api_statistics(stats)
                
                await status_msg.edit_text(status_text, parse_mode='HTML')
                logger.info(f"✅ Статистика отправлена (источник: Web API, {response_time}ms)")
                return
                
            except Exception as api_error:
                logger.warning(f"⚠️ Web API недоступен для /status, используем fallback: {api_error}")
        
        # Fallback: получаем статистику из БД напрямую
        from backend.models import User, Deadline
        from datetime import date
        
        stats = {}
        
        # Количество активных клиентов
        stats['active_clients_count'] = db_session.query(User).filter(
            User.role == 'client',
            User.is_active == True
        ).count()
        
        stats['total_clients_count'] = db_session.query(User).filter(
            User.role == 'client'
        ).count()
        
        # Количество дедлайнов по статусам
        all_deadlines = db_session.query(Deadline).filter(
            Deadline.status == 'active'
        ).all()
        
        stats['active_deadlines_count'] = len(all_deadlines)
        stats['total_deadlines_count'] = db_session.query(Deadline).count()
        
        # Подсчёт по статусам
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
        
        stats['status_green'] = green_count
        stats['status_yellow'] = yellow_count
        stats['status_red'] = red_count
        stats['status_expired'] = expired_count
        stats['data_source'] = 'database'
        
        # Форматируем статистику
        status_text = format_api_statistics(stats)
        
        await status_msg.edit_text(status_text, parse_mode='HTML')
        logger.info(f"✅ Статистика отправлена (источник: БД fallback)")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /status: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при получении статистики</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


@router.message(Command('health'))
async def cmd_health(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """
    НОВАЯ КОМАНДА: /health
    Проверка здоровья Web API и статуса подключения
    Доступна только администратору
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
    # Проверка прав администратора
    if not is_admin:
        logger.warning(f"⛔ Попытка /health от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"🏥 /health от администратора {user.id}")
    
    # Показываем индикатор проверки
    status_msg = await message.answer("🔍 Проверка Web API...", parse_mode='HTML')
    
    try:
        # Получаем API клиент из checker service
        api_client = checker._api_client
        
        if not api_client:
            await status_msg.edit_text(
                "⚠️ <b>Web API клиент не инициализирован</b>\n\n"
                "Бот работает в режиме прямого доступа к базе данных.",
                parse_mode='HTML'
            )
            return
        
        # Проверяем статус токена
        token_manager = api_client.token_manager
        token_valid = token_manager._is_token_valid() if hasattr(token_manager, '_is_token_valid') else False
        
        health_data = {
            'api_url': settings.web_api_base_url,
            'token_valid': token_valid,
            'api_available': False,
            'response_time': None,
            'error': None
        }
        
        # Проверяем доступность API
        try:
            start_time = time.time()
            stats = await api_client.get_dashboard_stats()
            response_time = int((time.time() - start_time) * 1000)
            
            health_data['api_available'] = True
            health_data['response_time'] = response_time
            health_data['stats'] = stats
            
        except Exception as api_error:
            health_data['error'] = str(api_error)
        
        # Форматируем результат проверки
        health_text = format_health_status(health_data)
        
        await status_msg.edit_text(health_text, parse_mode='HTML')
        logger.info(f"✅ Health check завершён: API {'доступен' if health_data['api_available'] else 'недоступен'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /health: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при проверке здоровья</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']