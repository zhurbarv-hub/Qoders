# -*- coding: utf-8 -*-
"""
Команда экспорта данных через Telegram бота
Экспорт клиентов, дедлайнов и статистики в JSON/CSV
"""
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from datetime import datetime

from bot.services.conversation import (
    start_conversation, get_conversation, end_conversation
)
from bot.services.api_client import WebAPIClient
from bot.services import checker

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('export'))
async def cmd_export(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """Команда /export - экспорт данных"""
    user = message.from_user
    
    # Проверка прав (админ или менеджер)
    if user_role not in ['admin', 'manager']:
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Только администратор или менеджер может экспортировать данные.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"📤 /export от {user_role} {user.id}")
    
    # Создаём клавиатуру выбора типа данных
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Клиенты", callback_data="export:clients"),
            InlineKeyboardButton(text="📅 Дедлайны", callback_data="export:deadlines")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="export:statistics")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="export:cancel")
        ]
    ])
    
    await message.answer(
        "📤 <b>Экспорт данных</b>\n\n"
        "Выберите, что хотите экспортировать:",
        reply_markup=keyboard,
        parse_mode='HTML'
    )


@router.callback_query(lambda c: c.data and c.data.startswith('export:'))
async def process_export_callback(
    callback: CallbackQuery,
    user_role: str = 'unknown',
    **kwargs
):
    """Обработка callback кнопок экспорта"""
    user = callback.from_user
    action = callback.data.split(':')[1]
    
    # Отмена
    if action == 'cancel':
        await callback.message.edit_text("❌ Экспорт отменён")
        await callback.answer()
        return
    
    # Показываем клавиатуру выбора формата
    if action in ['clients', 'deadlines', 'statistics']:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📄 JSON", callback_data=f"format:{action}:json"),
                InlineKeyboardButton(text="📊 CSV", callback_data=f"format:{action}:csv")
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="export:back"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="export:cancel")
            ]
        ])
        
        data_names = {
            'clients': 'клиентов',
            'deadlines': 'дедлайнов',
            'statistics': 'статистики'
        }
        
        await callback.message.edit_text(
            f"📤 <b>Экспорт {data_names[action]}</b>\n\n"
            f"Выберите формат:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        await callback.answer()
    
    # Возврат назад
    elif action == 'back':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👥 Клиенты", callback_data="export:clients"),
                InlineKeyboardButton(text="📅 Дедлайны", callback_data="export:deadlines")
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="export:statistics")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="export:cancel")
            ]
        ])
        
        await callback.message.edit_text(
            "📤 <b>Экспорт данных</b>\n\n"
            "Выберите, что хотите экспортировать:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        await callback.answer()


@router.callback_query(lambda c: c.data and c.data.startswith('format:'))
async def process_format_callback(
    callback: CallbackQuery,
    user_role: str = 'unknown',
    **kwargs
):
    """Обработка выбора формата и выполнение экспорта"""
    user = callback.from_user
    parts = callback.data.split(':')
    data_type = parts[1]  # clients, deadlines, statistics
    format_type = parts[2]  # json, csv
    
    await callback.answer("⏳ Экспортирую данные...")
    
    api_client = checker._api_client
    if not api_client:
        await callback.message.edit_text("⚠️ Web API недоступен")
        return
    
    try:
        # Формируем запрос к API
        endpoint = f"/api/export/{data_type}"
        params = {"format": format_type}
        
        # Добавляем фильтр для активных клиентов/дедлайнов
        if data_type == 'clients':
            params['is_active'] = True
        elif data_type == 'deadlines':
            params['status'] = 'active'
        
        # Получаем данные через API (как bytes)
        logger.info(f"Экспорт: {endpoint}?{params}")
        
        # Используем метод get_file для получения файла
        response = await api_client._request(
            method='GET',
            endpoint=endpoint,
            params=params
        )
        
        # response содержит bytes файла
        if not response:
            await callback.message.edit_text("❌ Нет данных для экспорта")
            return
        
        # Определяем имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extension = format_type
        filename = f"{data_type}_{timestamp}.{extension}"
        
        # Определяем MIME тип
        mime_type = "application/json" if format_type == 'json' else "text/csv"
        
        # Создаём файл для отправки
        file = BufferedInputFile(
            file=response,
            filename=filename
        )
        
        # Отправляем файл пользователю
        await callback.message.answer_document(
            document=file,
            caption=f"✅ <b>Экспорт завершён</b>\n\n"
                   f"📁 Тип: {data_type}\n"
                   f"📄 Формат: {format_type.upper()}\n"
                   f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            parse_mode='HTML'
        )
        
        # Удаляем сообщение с меню
        await callback.message.delete()
        
        logger.info(f"Экспорт выполнен: {filename} для user {user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка экспорта: {e}")
        await callback.message.edit_text(
            f"❌ <b>Ошибка экспорта</b>\n\n"
            f"Детали: {str(e)}\n\n"
            f"Попробуйте позже или обратитесь к администратору.",
            parse_mode='HTML'
        )


# Экспорт
__all__ = ['router']