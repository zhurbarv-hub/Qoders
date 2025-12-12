"""
Команды поиска информации через Web API
Поиск клиентов по ИНН, названию - теперь через Web API
"""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.services import checker

logger = logging.getLogger(__name__)

# Создаём роутер для команд поиска
router = Router()


@router.message(Command('search'))
async def cmd_search(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """
    Поиск клиента по ИНН или названию через Web API
    
    Использование:
        /search 1234567890 - поиск по ИНН
        /search ООО Ромашка - поиск по названию
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
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
            "🔍 Поиск по ИНН:\n"
            "<code>/search 1234567890</code>\n\n"
            "🔍 Поиск по названию:\n"
            "<code>/search ООО Ромашка</code>\n\n"
            "🔍 Частичный поиск:\n"
            "<code>/search Ромаш</code>\n\n"
            "💡 Совет: используйте /addclient для добавления нового клиента",
            parse_mode='HTML'
        )
        return
    
    search_query = args[1].strip()
    
    logger.info(f"🔍 Поиск клиента: query='{search_query}'")
    
    # Получаем API клиент
    api_client = checker._api_client
    if not api_client:
        await message.answer(
            "⚠️ <b>Web API недоступен</b>\n\n"
            "Поиск временно недоступен. Попробуйте позже.",
            parse_mode='HTML'
        )
        return
    
    try:
        # Поиск через Web API
        response = await api_client.get("/api/clients", params={"search": search_query})
        clients = response.get('clients', [])
        
        if not clients:
            await message.answer(
                f"❌ <b>Ничего не найдено</b>\n\n"
                f"По запросу: <code>{search_query}</code>\n\n"
                f"💡 Используйте /addclient для добавления нового клиента",
                parse_mode='HTML'
            )
            return
        
        # Формируем ответ для каждого найденного клиента
        for client in clients[:5]:  # Максимум 5 клиентов
            client_id = client['id']
            
            # Получаем дедлайны клиента через API
            try:
                deadlines = await api_client.get(f"/api/deadlines/by-client/{client_id}")
            except:
                deadlines = []
            
            # Фильтруем только активные
            active_deadlines = [d for d in deadlines if d.get('status') == 'active']
            
            # Формируем список дедлайнов
            from datetime import datetime, date
            deadlines_info = ""
            
            for d in active_deadlines[:5]:  # Максимум 5 дедлайнов
                try:
                    deadline_date = datetime.fromisoformat(d['deadline_date']).date()
                    days = (deadline_date - date.today()).days
                    
                    if days < 0:
                        emoji = "⚫"
                    elif days <= 3:
                        emoji = "🔴"
                    elif days <= 7:
                        emoji = "🟡"
                    else:
                        emoji = "🟢"
                    
                    deadlines_info += f"\n   {emoji} {d.get('deadline_type_name', 'Неизвестно')}: {deadline_date.strftime('%d.%m.%Y')} (через {days} дн.)"
                except:
                    continue
            
            if len(active_deadlines) > 5:
                deadlines_info += f"\n   <i>... и ещё {len(active_deadlines) - 5}</i>"
            
            # Формируем ответ
            response_text = f"""
🔍 <b>Результат поиска</b>

<b>📋 Клиент:</b>
• ID: {client['id']}
• Название: <b>{client['name']}</b>
• ИНН: <code>{client['inn']}</code>
• Email: {client.get('email') or 'не указан'}
• Телефон: {client.get('phone') or 'не указан'}
• Статус: {'✅ Активен' if client.get('is_active') else '❌ Неактивен'}

<b>📅 Активные дедлайны ({len(active_deadlines)}):</b>{deadlines_info if deadlines_info else '\n   <i>Нет дедлайнов</i>'}

<b>⚙️ Управление:</b>
• /editclient {client['inn']} - редактировать
• /adddeadline - добавить дедлайн
""".strip()
            
            await message.answer(response_text, parse_mode='HTML')
        
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
            "Попробуйте позже или обратитесь к администратору.",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']