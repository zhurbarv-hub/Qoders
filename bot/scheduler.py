"""
Планировщик автоматических задач Telegram бота
Настройка и управление фоновыми задачами (ежедневные проверки)
"""
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from sqlalchemy.orm import Session

from bot.services.notifier import process_deadline_notifications
from bot.services.api_client import WebAPIClient
from bot.services.exceptions import APIError, ConnectionError as APIConnectionError
from backend.config import settings

logger = logging.getLogger(__name__)


async def scheduled_deadline_check(bot: Bot, db_session: Session, api_client: WebAPIClient = None):
    """
    Запланированная проверка дедлайнов
    Вызывается автоматически по расписанию
    
    Args:
        bot: Экземпляр бота для отправки уведомлений
        db_session: Сессия базы данных
        api_client: API клиент для проверки здоровья (опционально)
    """
    logger.info("⏰ ЗАПУСК АВТОМАТИЧЕСКОЙ ПРОВЕРКИ ДЕДЛАЙНОВ")
    
    # Health check API перед началом проверки
    api_available = True
    if api_client:
        try:
            logger.info("🔍 Проверка доступности Web API...")
            stats = await api_client.get_dashboard_stats()
            logger.info(f"✅ Web API доступен. Активных дедлайнов: {stats.get('active_deadlines_count', 0)}")
        except (APIError, APIConnectionError, Exception) as e:
            logger.warning(f"⚠️ Web API недоступен, будет использован fallback: {e}")
            api_available = False
    
    try:
        # Получаем дни для проверки из конфигурации
        days_list = settings.notification_days_list
        
        total_stats = {
            'checked': 0,
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'api_used': api_available
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
        
        logger.info(
            f"✅ Автоматическая проверка завершена: "
            f"проверено={total_stats['checked']}, "
            f"отправлено={total_stats['sent']}, "
            f"пропущено={total_stats['skipped']}, "
            f"ошибок={total_stats['failed']}"
        )
        
        # Уведомляем администратора о результатах
        if total_stats['sent'] > 0 or total_stats['failed'] > 0:
            # Добавляем информацию об источнике данных
            data_source = "🔌 Web API" if api_available else "💾 База данных (fallback)"
            
            report = f"""
🔔 <b>Автоматическая проверка завершена</b>

📊 <b>Результаты:</b>
• Проверено: {total_stats['checked']}
• Отправлено: {total_stats['sent']}
• Пропущено: {total_stats['skipped']}
• Ошибок: {total_stats['failed']}

📡 <b>Источник данных:</b> {data_source}
⏰ <b>Время проверки:</b> {datetime.now().strftime('%H:%M:%S')}
""".strip()
            
            try:
                await bot.send_message(
                    chat_id=settings.telegram_admin_id,
                    text=report,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"❌ Не удалось отправить отчёт администратору: {e}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при автоматической проверке: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Уведомляем администратора об ошибке
        try:
            await bot.send_message(
                chat_id=settings.telegram_admin_id,
                text=f"❌ <b>Ошибка автоматической проверки</b>\n\n<code>{str(e)[:200]}</code>",
                parse_mode='HTML'
            )
        except:
            pass


def setup_scheduler(bot: Bot, db_session: Session, api_client: WebAPIClient = None) -> AsyncIOScheduler:
    """
    Настройка и запуск планировщика задач
    
    Args:
        bot: Экземпляр бота
        db_session: Сессия базы данных
        api_client: API клиент для health checks (опционально)
        
    Returns:
        AsyncIOScheduler: Настроенный планировщик
    """
    scheduler = AsyncIOScheduler(timezone=settings.notification_timezone)
    
    # Парсим время из конфигурации (формат "HH:MM")
    time_parts = settings.notification_check_time.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    
    # Создаём cron-триггер для ежедневного запуска
    trigger = CronTrigger(
        hour=hour,
        minute=minute,
        timezone=settings.notification_timezone
    )
    
    # Добавляем задачу в планировщик
    scheduler.add_job(
        scheduled_deadline_check,
        trigger=trigger,
        args=[bot, db_session, api_client],  # Передаём api_client
        id='deadline_check',
        name='Ежедневная проверка дедлайнов',
        replace_existing=True
    )
    
    logger.info(
        f"📅 Планировщик настроен: проверка каждый день в {settings.notification_check_time} "
        f"({settings.notification_timezone})"
    )
    logger.info(f"📋 Дни уведомлений: {', '.join(map(str, settings.notification_days_list))}")
    
    if api_client:
        logger.info(f"🔌 Web API интеграция включена")
    else:
        logger.warning(f"⚠️ API клиент не передан, будет использоваться только БД")
    
    return scheduler


# Экспорт функций
__all__ = ['setup_scheduler', 'scheduled_deadline_check']