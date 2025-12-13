"""
Команды поиска клиентов по названию, ИНН
Поддерживает частичный поиск по названию компании
"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import date
from sqlalchemy.orm import Session

from backend.models import User, Deadline, DeadlineType
from bot.services import checker

logger = logging.getLogger(__name__)

# Создаём роутер для команд поиска
router = Router()


def find_client_by_name_or_inn(db_session: Session, search_query: str):
    """
    Поиск клиента по названию компании, части названия или ИНН
    
    Args:
        db_session: Сессия базы данных
        search_query: Строка поиска
        
    Returns:
        Список найденных клиентов
    """
    search_pattern = f"%{search_query}%"
    
    # Пытаемся найти по ИНН (точное совпадение) или по названию (частичное)
    clients = db_session.query(User).filter(
        User.role == 'client',
        User.is_active == True,
        (User.company_name.ilike(search_pattern)) | (User.inn.ilike(search_pattern))
    ).all()
    
    return clients


@router.message(Command('search'))
async def cmd_search(
    message: Message,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    Поиск клиента по названию компании или ИНН
    
    Использование:
        /search 1234567890 - поиск по ИНН
        /search ООО Ромашка - поиск по названию
        /search Ромаш - частичный поиск по названию
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных из middleware
    """
    user = message.from_user
    
    # Только для администратора и менеджера
    if user_role not in ['admin', 'manager']:
        logger.warning(f"⛔ Попытка /search от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору и менеджеру.",
            parse_mode='HTML'
        )
        return
    
    # Парсим аргументы
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        await message.answer(
            "ℹ️ <b>Использование команды /search</b>\n\n"
            "🔍 <b>Поиск по ИНН:</b>\n"
            "<code>/search 1234567890</code>\n\n"
            "🔍 <b>Поиск по названию:</b>\n"
            "<code>/search ООО Ромашка</code>\n\n"
            "🔍 <b>Частичный поиск:</b>\n"
            "<code>/search Ромаш</code>\n\n"
            "💡 Поиск ищет совпадения в названии компании и ИНН\n"
            "💡 Для просмотра карточки клиента: /client <название>",
            parse_mode='HTML'
        )
        return
    
    search_query = args[1].strip()
    
    logger.info(f"🔍 /search от {user_role} {user.id}: query='{search_query}'")
    
    # Поиск в базе данных
    try:
        found_clients = find_client_by_name_or_inn(db_session, search_query)
        
        if not found_clients:
            await message.answer(
                f"❌ <b>Ничего не найдено</b>\n\n"
                f"По запросу: <code>{search_query}</code>\n\n"
                f"💡 Проверьте правильность написания\n"
                f"💡 Попробуйте использовать часть названия или ИНН",
                parse_mode='HTML'
            )
            logger.info(f"❌ Поиск не дал результатов: '{search_query}'")
            return
        
        # Если найдено слишком много результатов - показываем список
        if len(found_clients) > 10:
            clients_list = "\n".join([
                f"• /client {c.id} - {c.company_name} (ИНН: {c.inn or 'не указан'})"
                for c in found_clients[:20]
            ])
            
            await message.answer(
                f"🔍 <b>Найдено клиентов: {len(found_clients)}</b>\n\n"
                f"Показаны первые 20 результатов:\n\n"
                f"{clients_list}\n\n"
                f"💡 Уточните запрос для более точного поиска\n"
                f"💡 Нажмите на команду /client для просмотра карточки",
                parse_mode='HTML'
            )
            logger.info(f"✅ Поиск выполнен: найдено {len(found_clients)} клиентов (показано 20)")
            return
        
        # Формируем подробную информацию для каждого найденного клиента (до 10 шт)
        for client in found_clients[:10]:
            # Получаем активные дедлайны клиента
            active_deadlines = db_session.query(Deadline).join(
                DeadlineType
            ).filter(
                Deadline.user_id == client.id,
                Deadline.status == 'active'
            ).order_by(
                Deadline.deadline_date
            ).all()
            
            # Формируем список дедлайнов
            deadlines_info = ""
            for d in active_deadlines[:5]:  # Максимум 5 дедлайнов
                days = (d.deadline_date - date.today()).days
                
                if days < 0:
                    emoji = "⚫"
                elif days <= 3:
                    emoji = "🔴"
                elif days <= 7:
                    emoji = "🟡"
                else:
                    emoji = "🟢"
                
                deadlines_info += f"\n   {emoji} {d.deadline_type.name}: {d.deadline_date.strftime('%d.%m.%Y')} (через {days} дн.)"
            
            if len(active_deadlines) > 5:
                deadlines_info += f"\n   <i>... и ещё {len(active_deadlines) - 5}</i>"
            
            # Формируем ответ
            response_text = f"""
🔍 <b>Результат поиска</b>

<b>📋 Клиент:</b>
• ID: {client.id}
• Название: <b>{client.company_name}</b>
• ИНН: <code>{client.inn or 'не указан'}</code>
• Email: {client.email or 'не указан'}
• Телефон: {client.phone or 'не указан'}
• Статус: {'✅ Активен' if client.is_active else '❌ Неактивен'}

<b>📅 Активные дедлайны ({len(active_deadlines)}):</b>{deadlines_info if deadlines_info else '\n   <i>Нет дедлайнов</i>'}

<b>⚙️ Управление:</b>
• /client {client.id} - полная карточка клиента
• /filter {client.id} - фильтр дедлайнов по клиенту
""".strip()
            
            await message.answer(response_text, parse_mode='HTML')
        
        if len(found_clients) > 10:
            await message.answer(
                f"ℹ️ Показано 10 из {len(found_clients)} результатов.\n"
                f"Уточните запрос для более точного поиска.",
                parse_mode='HTML'
            )
        
        logger.info(f"✅ Поиск выполнен: найдено {len(found_clients)} клиентов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при поиске: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "❌ <b>Ошибка поиска</b>\n\n"
            "Попробуйте позже или обратитесь к администратору.",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']