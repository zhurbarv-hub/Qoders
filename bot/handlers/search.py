"""
Команды поиска информации (только для администратора)
Поиск клиентов по ИНН, названию и другим параметрам
"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from backend.models import Client, Deadline, Contact
from bot.services.formatter import format_deadline_list

logger = logging.getLogger(__name__)

# Создаём роутер для команд поиска
router = Router()


@router.message(Command('search'))
async def cmd_search(
    message: Message,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    Поиск клиента по ИНН или названию
    
    Использование:
        /search 1234567890 - поиск по ИНН
        /search ООО Ромашка - поиск по названию
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
    # Только для администратора
    if not is_admin:
        logger.warning(f"⛔ Попытка /search от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору.",
            parse_mode='HTML'
        )
        return
    
    # Парсим аргументы
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "ℹ️ <b>Использование команды /search</b>\n\n"
            "🔍 Поиск по ИНН:\n"
            "<code>/search 1234567890</code>\n\n"
            "🔍 Поиск по названию:\n"
            "<code>/search ООО Ромашка</code>\n\n"
            "🔍 Частичный поиск:\n"
            "<code>/search Ромаш</code>",
            parse_mode='HTML'
        )
        return
    
    search_query = args[1].strip()
    
    logger.info(f"🔍 Поиск клиента: query='{search_query}'")
    
    try:
        # Определяем тип поиска (по ИНН или названию)
        if search_query.isdigit():
            # Поиск по ИНН
            clients = db_session.query(Client).filter(
                Client.inn.like(f'%{search_query}%')
            ).all()
            search_type = "ИНН"
        else:
            # Поиск по названию
            clients = db_session.query(Client).filter(
                Client.name.ilike(f'%{search_query}%')
            ).all()
            search_type = "названию"
        
        if not clients:
            await message.answer(
                f"❌ <b>Ничего не найдено</b>\n\n"
                f"По запросу: <code>{search_query}</code>\n"
                f"Тип поиска: {search_type}",
                parse_mode='HTML'
            )
            return
        
        # Формируем ответ для каждого найденного клиента
        for client in clients[:5]:  # Максимум 5 клиентов
            # Получаем дедлайны клиента
            deadlines = db_session.query(Deadline).filter(
                Deadline.client_id == client.id,
                Deadline.status == 'active'
            ).all()
            
            # Получаем контакты
            contacts = db_session.query(Contact).filter(
                Contact.client_id == client.id
            ).all()
            
            # Формируем информацию о контактах
            contacts_info = ""
            for contact in contacts:
                status = "🔔" if contact.notifications_enabled else "🔕"
                tg_id = contact.telegram_id or "не указан"
                contacts_info += f"\n   {status} {contact.name}: <code>{tg_id}</code>"
            
            # Формируем список дедлайнов
            from datetime import date
            deadlines_info = ""
            for d in deadlines[:5]:  # Максимум 5 дедлайнов
                days = (d.expiration_date - date.today()).days
                
                if days < 0:
                    emoji = "⚫"
                elif days <= 3:
                    emoji = "🔴"
                elif days <= 7:
                    emoji = "🟡"
                else:
                    emoji = "🟢"
                
                deadlines_info += f"\n   {emoji} {d.deadline_type.type_name}: {d.expiration_date.strftime('%d.%m.%Y')} (через {days} дн.)"
            
            if len(deadlines) > 5:
                deadlines_info += f"\n   <i>... и ещё {len(deadlines) - 5}</i>"
            
            # Формируем ответ
            response = f"""
🔍 <b>Результат поиска</b>

<b>📋 Клиент:</b>
• Название: <b>{client.name}</b>
• ИНН: <code>{client.inn}</code>
• Статус: {'✅ Активен' if client.is_active else '❌ Неактивен'}

<b>👥 Контакты:</b>{contacts_info if contacts_info else '\n   <i>Нет контактов</i>'}

<b>📅 Активные дедлайны ({len(deadlines)}):</b>{deadlines_info if deadlines_info else '\n   <i>Нет дедлайнов</i>'}
""".strip()
            
            await message.answer(response, parse_mode='HTML')
        
        if len(clients) > 5:
            await message.answer(
                f"ℹ️ Показано 5 из {len(clients)} результатов.\n"
                f"Уточните запрос для более точного поиска.",
                parse_mode='HTML'
            )
        
        logger.info(f"✅ Поиск выполнен: найдено {len(clients)} клиентов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при поиске: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "❌ <b>Ошибка поиска</b>\n\n"
            "Попробуйте позже или обратитесь к разработчику.",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']