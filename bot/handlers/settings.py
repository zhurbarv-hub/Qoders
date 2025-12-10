"""
Команды управления настройками пользователя
Управление уведомлениями, экспорт данных
"""
import logging
import json
from datetime import datetime, timedelta, date
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from sqlalchemy.orm import Session

from backend.models import Contact, Client, Deadline
from bot.services.formatter import format_deadline_list

logger = logging.getLogger(__name__)

# Создаём роутер для команд настроек
router = Router()


@router.message(Command('mute'))
async def cmd_mute(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    db_session: Session = None,
    **kwargs
):
    """
    Временно отключить уведомления
    
    Использование:
        /mute - отключить на 7 дней
        /mute 3 - отключить на 3 дня
        /mute 30 - отключить на 30 дней
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя
        client_id: ID клиента
        db_session: Сессия базы данных
    """
    user = message.from_user
    
    # Только клиенты могут управлять своими уведомлениями
    if user_role != 'client':
        await message.answer(
            "❌ <b>Команда недоступна</b>\n\n"
            "Эта команда доступна только для клиентов.",
            parse_mode='HTML'
        )
        return
    
    # Парсим количество дней из аргументов
    args = message.text.split()
    days = 7  # По умолчанию 7 дней
    
    if len(args) > 1:
        try:
            days = int(args[1])
            if days < 1 or days > 365:
                await message.answer(
                    "❌ <b>Некорректное количество дней</b>\n\n"
                    "Укажите число от 1 до 365.",
                    parse_mode='HTML'
                )
                return
        except ValueError:
            await message.answer(
                "❌ <b>Некорректный формат</b>\n\n"
                "Использование: <code>/mute [дни]</code>\n"
                "Пример: <code>/mute 7</code>",
                parse_mode='HTML'
            )
            return
    
    try:
        # Находим контакт пользователя
        contact = db_session.query(Contact).filter(
            Contact.client_id == client_id,
            Contact.telegram_id == str(user.id)
        ).first()
        
        if not contact:
            await message.answer(
                "❌ <b>Контакт не найден</b>\n\n"
                "Обратитесь к администратору.",
                parse_mode='HTML'
            )
            return
        
        # Отключаем уведомления
        contact.notifications_enabled = False
        contact.muted_until = datetime.now() + timedelta(days=days)
        db_session.commit()
        
        muted_until = contact.muted_until.strftime('%d.%m.%Y %H:%M')
        
        await message.answer(
            f"🔕 <b>Уведомления отключены</b>\n\n"
            f"⏰ До: <b>{muted_until}</b>\n"
            f"📅 На {days} дн.\n\n"
            f"Для включения используйте /unmute",
            parse_mode='HTML'
        )
        
        logger.info(f"🔕 Уведомления отключены: user_id={user.id}, days={days}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отключении уведомлений: {e}")
        await message.answer(
            "❌ <b>Ошибка</b>\n\n"
            "Не удалось отключить уведомления. Попробуйте позже.",
            parse_mode='HTML'
        )


@router.message(Command('unmute'))
async def cmd_unmute(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    db_session: Session = None,
    **kwargs
):
    """
    Включить уведомления обратно
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя
        client_id: ID клиента
        db_session: Сессия базы данных
    """
    user = message.from_user
    
    if user_role != 'client':
        await message.answer(
            "❌ <b>Команда недоступна</b>\n\n"
            "Эта команда доступна только для клиентов.",
            parse_mode='HTML'
        )
        return
    
    try:
        # Находим контакт пользователя
        contact = db_session.query(Contact).filter(
            Contact.client_id == client_id,
            Contact.telegram_id == str(user.id)
        ).first()
        
        if not contact:
            await message.answer(
                "❌ <b>Контакт не найден</b>",
                parse_mode='HTML'
            )
            return
        
        # Включаем уведомления
        contact.notifications_enabled = True
        contact.muted_until = None
        db_session.commit()
        
        await message.answer(
            "🔔 <b>Уведомления включены</b>\n\n"
            "Вы снова будете получать уведомления о приближающихся сроках.",
            parse_mode='HTML'
        )
        
        logger.info(f"🔔 Уведомления включены: user_id={user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при включении уведомлений: {e}")
        await message.answer(
            "❌ <b>Ошибка</b>\n\n"
            "Не удалось включить уведомления.",
            parse_mode='HTML'
        )


@router.message(Command('settings'))
async def cmd_settings(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    client_name: str = None,
    db_session: Session = None,
    **kwargs
):
    """
    Показать текущие настройки уведомлений
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя
        client_id: ID клиента
        client_name: Название клиента
        db_session: Сессия базы данных
    """
    user = message.from_user
    
    if user_role == 'unknown':
        await message.answer(
            "❌ <b>Вы не авторизованы</b>\n\n"
            "Обратитесь к администратору для получения доступа.",
            parse_mode='HTML'
        )
        return
    
    try:
        if user_role == 'admin':
            # Для администратора показываем общую информацию
            from backend.config import settings
            
            response = f"""
⚙️ <b>Настройки системы</b>

<b>📅 Планировщик:</b>
• Время проверки: <b>{settings.notification_check_time}</b>
• Часовой пояс: <b>{settings.notification_timezone}</b>
• Дни уведомлений: <b>{', '.join(map(str, settings.notification_days_list))}</b>

<b>🔄 Повторные попытки:</b>
• Максимум попыток: <b>{settings.notification_retry_attempts}</b>
• Задержка: <b>{settings.notification_retry_delay // 60} мин</b>
""".strip()
            
        else:
            # Для клиента показываем его настройки
            contact = db_session.query(Contact).filter(
                Contact.client_id == client_id,
                Contact.telegram_id == str(user.id)
            ).first()
            
            if not contact:
                await message.answer("❌ <b>Контакт не найден</b>", parse_mode='HTML')
                return
            
            # Статус уведомлений
            if contact.notifications_enabled:
                status = "✅ Включены"
                mute_info = ""
            else:
                status = "🔕 Отключены"
                if contact.muted_until:
                    muted_until = contact.muted_until.strftime('%d.%m.%Y %H:%M')
                    mute_info = f"\n• До: <b>{muted_until}</b>"
                else:
                    mute_info = ""
            
            # Количество активных дедлайнов
            deadlines_count = db_session.query(Deadline).filter(
                Deadline.client_id == client_id,
                Deadline.status == 'active'
            ).count()
            
            response = f"""
⚙️ <b>Ваши настройки</b>

<b>👤 Клиент:</b>
• Организация: <b>{client_name}</b>
• Telegram ID: <code>{user.id}</code>

<b>🔔 Уведомления:</b>
• Статус: {status}{mute_info}

<b>📊 Активные дедлайны:</b>
• Всего: <b>{deadlines_count}</b>

<i>💡 Используйте /mute для отключения уведомлений
или /unmute для включения</i>
""".strip()
        
        await message.answer(response, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении настроек: {e}")
        await message.answer(
            "❌ <b>Ошибка</b>\n\n"
            "Не удалось получить настройки.",
            parse_mode='HTML'
        )


@router.message(Command('export'))
async def cmd_export(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    client_name: str = None,
    db_session: Session = None,
    **kwargs
):
    """
    Экспорт данных клиента в JSON
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя
        client_id: ID клиента
        client_name: Название клиента
        db_session: Сессия базы данных
    """
    if user_role == 'unknown':
        await message.answer(
            "❌ <b>Вы не авторизованы</b>",
            parse_mode='HTML'
        )
        return
    
    try:
        # Получаем дедлайны клиента
        deadlines_query = db_session.query(Deadline).filter(
            Deadline.status == 'active'
        )
        
        if user_role == 'client':
            deadlines_query = deadlines_query.filter(Deadline.client_id == client_id)
        
        deadlines = deadlines_query.all()
        
        # Формируем JSON
        export_data = {
            'export_date': datetime.now().isoformat(),
            'client_name': client_name if user_role == 'client' else 'All Clients',
            'deadlines_count': len(deadlines),
            'deadlines': []
        }
        
        for d in deadlines:
            export_data['deadlines'].append({
                'id': d.id,
                'client_name': d.client.name,
                'client_inn': d.client.inn,
                'deadline_type': d.deadline_type.type_name,
                'expiration_date': d.expiration_date.isoformat(),
                'days_remaining': (d.expiration_date - date.today()).days,
                'notes': d.notes,
                'status': d.status,
                'created_at': d.created_at.isoformat() if d.created_at else None
            })
        
        # Создаём временный файл
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = f"logs/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        # Отправляем файл
        await message.answer_document(
            document=FSInputFile(filepath),
            caption=f"📊 <b>Экспорт данных</b>\n\nВсего дедлайнов: {len(deadlines)}",
            parse_mode='HTML'
        )
        
        logger.info(f"📊 Экспорт данных: user_id={message.from_user.id}, count={len(deadlines)}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при экспорте: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "❌ <b>Ошибка экспорта</b>\n\n"
            "Не удалось создать файл. Попробуйте позже.",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']