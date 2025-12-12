# -*- coding: utf-8 -*-
"""
Команды управления клиентами через Telegram бота
CRUD операции: создание, редактирование, удаление клиентов
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from bot.services.validators import (
    validate_inn, validate_client_name, validate_phone, 
    validate_email, validate_yes_no
)
from bot.services.conversation import (
    start_conversation, get_conversation, 
    end_conversation, cancel_conversation
)
from bot.services.api_client import WebAPIClient
from bot.services import checker

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('addclient'))
async def cmd_addclient(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """Команда /addclient - добавить нового клиента"""
    user = message.from_user
    
    # Проверка прав (только админ)
    if user_role != 'admin':
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Только администратор может добавлять клиентов.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"📝 /addclient от admin {user.id}")
    
    # Начало диалога
    conv = start_conversation(user.id, 'add_client')
    conv.next_step()
    
    await message.answer(
        "📝 <b>Добавление нового клиента</b>\n\n"
        "<b>Шаг 1/7:</b> Введите название организации:\n\n"
        "Используйте /cancel для отмены",
        parse_mode='HTML'
    )


@router.message(Command('editclient'))
async def cmd_editclient(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """Команда /editclient <ИНН> - редактировать клиента"""
    user = message.from_user
    
    if user_role != 'admin':
        await message.answer("❌ Только администратор может редактировать клиентов.", parse_mode='HTML')
        return
    
    # Парсинг ИНН из команды
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "⚠️ <b>Неверный формат</b>\n\n"
            "Использование: <code>/editclient ИНН</code>\n"
            "Пример: <code>/editclient 1234567890</code>",
            parse_mode='HTML'
        )
        return
    
    inn = parts[1].strip()
    
    # Валидация ИНН
    validation = validate_inn(inn)
    if not validation.valid:
        await message.answer(f"❌ {validation.error_message}", parse_mode='HTML')
        return
    
    # Поиск клиента через API
    api_client = checker._api_client
    if not api_client:
        await message.answer("⚠️ Web API недоступен", parse_mode='HTML')
        return
    
    try:
        # Поиск по ИНН
        response = await api_client.get("/api/clients", params={"search": validation.cleaned_value})
        clients = response.get('clients', [])
        
        if not clients:
            await message.answer(f"❌ Клиент с ИНН {validation.cleaned_value} не найден", parse_mode='HTML')
            return
        
        client = clients[0]
        
        # Начало диалога редактирования
        conv = start_conversation(user.id, 'edit_client')
        conv.set_data('client_id', client['id'])
        conv.set_data('client', client)
        conv.next_step()
        
        # Показываем текущие данные и меню
        await message.answer(
            f"📝 <b>Редактирование клиента</b>\n\n"
            f"🆔 ID: {client['id']}\n"
            f"📄 Название: {client['name']}\n"
            f"🏢 ИНН: {client['inn']}\n"
            f"📧 Email: {client.get('email') or 'не указан'}\n"
            f"📞 Телефон: {client.get('phone') or 'не указан'}\n"
            f"{'✅' if client.get('is_active') else '❌'} Статус: {'Активен' if client.get('is_active') else 'Неактивен'}\n\n"
            f"<b>Что хотите изменить?</b>\n"
            f"1️⃣ Название\n"
            f"2️⃣ Email\n"
            f"3️⃣ Телефон\n"
            f"4️⃣ Статус\n"
            f"❌ /cancel - Отмена",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Ошибка поиска клиента: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')


@router.message(Command('deleteclient'))
async def cmd_deleteclient(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """Команда /deleteclient <ИНН> - удалить клиента"""
    user = message.from_user
    
    if user_role != 'admin':
        await message.answer("❌ Только администратор может удалять клиентов.", parse_mode='HTML')
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "⚠️ Использование: <code>/deleteclient ИНН</code>",
            parse_mode='HTML'
        )
        return
    
    inn = parts[1].strip()
    validation = validate_inn(inn)
    if not validation.valid:
        await message.answer(f"❌ {validation.error_message}", parse_mode='HTML')
        return
    
    # Поиск клиента
    api_client = checker._api_client
    if not api_client:
        await message.answer("⚠️ Web API недоступен", parse_mode='HTML')
        return
    
    try:
        response = await api_client.get("/api/clients", params={"search": validation.cleaned_value})
        clients = response.get('clients', [])
        
        if not clients:
            await message.answer(f"❌ Клиент с ИНН {validation.cleaned_value} не найден", parse_mode='HTML')
            return
        
        client = clients[0]
        client_id = client['id']
        
        # Проверка активных дедлайнов
        deadlines_response = await api_client.get(f"/api/deadlines/by-client/{client_id}")
        active_count = len(deadlines_response) if deadlines_response else 0
        
        # Начало диалога удаления
        conv = start_conversation(user.id, 'delete_client')
        conv.set_data('client_id', client_id)
        conv.set_data('client', client)
        conv.set_data('inn', validation.cleaned_value)
        conv.next_step()
        
        warning = f"\n⚠️ У клиента {active_count} активных дедлайнов!\n" if active_count > 0 else ""
        
        await message.answer(
            f"⚠️ <b>УДАЛЕНИЕ КЛИЕНТА</b>\n\n"
            f"📄 Название: {client['name']}\n"
            f"🏢 ИНН: {client['inn']}\n"
            f"{warning}\n"
            f"Клиент будет деактивирован (данные сохранятся).\n\n"
            f"Для подтверждения введите: <code>УДАЛИТЬ {validation.cleaned_value}</code>",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Ошибка поиска клиента для удаления: {e}")
        await message.answer(f"❌ Ошибка: {str(e)}", parse_mode='HTML')


@router.message(Command('cancel'))
async def cmd_cancel(message: Message, **kwargs):
    """Команда /cancel - отменить текущий диалог"""
    user = message.from_user
    
    command = cancel_conversation(user.id)
    
    if command:
        logger.info(f"Диалог отменён: user {user.id}, команда {command}")
        await message.answer(
            "❌ <b>Операция отменена</b>",
            parse_mode='HTML'
        )
    else:
        await message.answer(
            "ℹ️ Нет активной операции для отмены",
            parse_mode='HTML'
        )

# Экспорт
__all__ = ['router']