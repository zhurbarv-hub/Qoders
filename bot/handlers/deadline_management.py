# -*- coding: utf-8 -*-
"""
Команды управления дедлайнами через Telegram бота
CRUD операции: создание, редактирование, удаление дедлайнов
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime

from bot.services.validators import (
    validate_inn, validate_date, validate_deadline_type_id, 
    validate_yes_no
)
from bot.services.conversation import (
    start_conversation, get_conversation, 
    end_conversation, cancel_conversation
)
from bot.services.api_client import WebAPIClient
from bot.services import checker

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('adddeadline'))
async def cmd_adddeadline(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """Команда /adddeadline - добавить новый дедлайн"""
    user = message.from_user
    
    # Проверка прав (админ или менеджер)
    if user_role not in ['admin', 'manager']:
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Только администратор или менеджер может добавлять дедлайны.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"📝 /adddeadline от {user_role} {user.id}")
    
    # Начало диалога
    conv = start_conversation(user.id, 'add_deadline')
    conv.next_step()
    
    await message.answer(
        "📝 <b>Добавление нового дедлайна</b>\n\n"
        "<b>Шаг 1/4:</b> Введите ИНН клиента или используйте /search для поиска:\n\n"
        "Используйте /cancel для отмены",
        parse_mode='HTML'
    )


@router.message(Command('editdeadline'))
async def cmd_editdeadline(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """Команда /editdeadline <ID> - редактировать дедлайн"""
    user = message.from_user
    
    if user_role not in ['admin', 'manager']:
        await message.answer("❌ Только администратор или менеджер может редактировать дедлайны.", parse_mode='HTML')
        return
    
    # Парсинг ID из команды
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "⚠️ <b>Неверный формат</b>\n\n"
            "Использование: <code>/editdeadline ID</code>\n"
            "Пример: <code>/editdeadline 15</code>",
            parse_mode='HTML'
        )
        return
    
    try:
        deadline_id = int(parts[1].strip())
    except ValueError:
        await message.answer("❌ ID должен быть числом", parse_mode='HTML')
        return
    
    # Поиск дедлайна через API
    api_client = checker._api_client
    if not api_client:
        await message.answer("⚠️ Web API недоступен", parse_mode='HTML')
        return
    
    try:
        # Получение дедлайна
        deadline = await api_client.get(f"/api/deadlines/{deadline_id}")
        
        if not deadline:
            await message.answer(f"❌ Дедлайн с ID {deadline_id} не найден", parse_mode='HTML')
            return
        
        # Начало диалога редактирования
        conv = start_conversation(user.id, 'edit_deadline')
        conv.set_data('deadline_id', deadline['id'])
        conv.set_data('deadline', deadline)
        conv.next_step()
        
        # Показываем текущие данные и меню
        status_emoji = "✅" if deadline.get('status') == 'active' else "❌" if deadline.get('status') == 'expired' else "✔️"
        
        await message.answer(
            f"📝 <b>Редактирование дедлайна</b>\n\n"
            f"🆔 ID: {deadline['id']}\n"
            f"🏢 Клиент: {deadline.get('client_name', 'Неизвестен')}\n"
            f"📋 Тип: {deadline.get('deadline_type_name', 'Неизвестен')}\n"
            f"📅 Дата: {deadline.get('deadline_date')}\n"
            f"📝 Примечание: {deadline.get('notes') or 'нет'}\n"
            f"{status_emoji} Статус: {deadline.get('status', 'unknown')}\n\n"
            f"<b>Что хотите изменить?</b>\n"
            f"1️⃣ Дата дедлайна\n"
            f"2️⃣ Примечание\n"
            f"3️⃣ Статус (пометить выполненным)\n"
            f"❌ /cancel - Отмена",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Ошибка поиска дедлайна: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')


@router.message(Command('deletedeadline'))
async def cmd_deletedeadline(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """Команда /deletedeadline <ID> - удалить дедлайн"""
    user = message.from_user
    
    if user_role != 'admin':
        await message.answer("❌ Только администратор может удалять дедлайны.", parse_mode='HTML')
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "⚠️ Использование: <code>/deletedeadline ID</code>",
            parse_mode='HTML'
        )
        return
    
    try:
        deadline_id = int(parts[1].strip())
    except ValueError:
        await message.answer("❌ ID должен быть числом", parse_mode='HTML')
        return
    
    # Поиск дедлайна
    api_client = checker._api_client
    if not api_client:
        await message.answer("⚠️ Web API недоступен", parse_mode='HTML')
        return
    
    try:
        deadline = await api_client.get(f"/api/deadlines/{deadline_id}")
        
        if not deadline:
            await message.answer(f"❌ Дедлайн с ID {deadline_id} не найден", parse_mode='HTML')
            return
        
        # Начало диалога удаления
        conv = start_conversation(user.id, 'delete_deadline')
        conv.set_data('deadline_id', deadline_id)
        conv.set_data('deadline', deadline)
        conv.next_step()
        
        await message.answer(
            f"⚠️ <b>УДАЛЕНИЕ ДЕДЛАЙНА</b>\n\n"
            f"🆔 ID: {deadline['id']}\n"
            f"🏢 Клиент: {deadline.get('client_name', 'Неизвестен')}\n"
            f"📋 Тип: {deadline.get('deadline_type_name', 'Неизвестен')}\n"
            f"📅 Дата: {deadline.get('deadline_date')}\n\n"
            f"Дедлайн будет удалён из системы.\n\n"
            f"Для подтверждения введите: <code>УДАЛИТЬ {deadline_id}</code>",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Ошибка поиска дедлайна для удаления: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')

# Экспорт
__all__ = ['router']