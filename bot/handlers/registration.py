# -*- coding: utf-8 -*-
"""
Обработчик авторизации клиентов в Telegram боте
Реализует двухэтапный процесс авторизации через регистрационный код
"""

import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session

from backend.models import User
from backend.database import SessionLocal
from backend.config import settings

logger = logging.getLogger(__name__)

# Создаём роутер для регистрации
router = Router()


class RegistrationStates(StatesGroup):
    """Состояния процесса регистрации"""
    waiting_for_code = State()


async def start_registration(message: Message, state: FSMContext):
    """
    Начало процесса регистрации клиента
    
    Args:
        message: Сообщение от пользователя
        state: Состояние FSM
    """
    await state.set_state(RegistrationStates.waiting_for_code)
    
    welcome_message = """
👋 <b>Добро пожаловать!</b>

Для начала работы с ботом необходимо пройти авторизацию.

🔐 Введите <b>6-значный код регистрации</b>, который вы получили от администратора.

💡 Код действителен в течение 72 часов с момента создания.

❓ Если у вас нет кода, обратитесь к администратору системы.
"""
    
    await message.answer(welcome_message, parse_mode='HTML')
    logger.info(f"Пользователь {message.from_user.id} начал процесс регистрации")


@router.message(RegistrationStates.waiting_for_code)
async def process_registration_code(message: Message, state: FSMContext):
    """
    Обработка введённого кода регистрации
    
    Args:
        message: Сообщение с кодом от пользователя
        state: Состояние FSM
    """
    code = message.text.strip().upper()
    telegram_id = str(message.from_user.id)
    telegram_username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    logger.info(f"Попытка регистрации пользователя {telegram_id} с кодом: {code}")
    
    # Валидация формата кода
    if len(code) != settings.registration_code_length:
        await message.answer(
            f"❌ Неверный формат кода\n\n"
            f"Код должен содержать {settings.registration_code_length} символов.\n"
            f"Попробуйте ещё раз или нажмите /start для выхода.",
            parse_mode='HTML'
        )
        return
    
    # Поиск пользователя с таким кодом
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(
            User.registration_code == code,
            User.telegram_id == None,  # Ещё не зарегистрирован
            User.role == 'client'
        ).first()
        
        if not user:
            logger.warning(f"Код {code} не найден или уже использован")
            await message.answer(
                "❌ <b>Неверный код регистрации</b>\n\n"
                "Возможные причины:\n"
                "• Код введён неправильно\n"
                "• Код уже был использован\n"
                "• Код не существует\n\n"
                "Попробуйте ещё раз или обратитесь к администратору.",
                parse_mode='HTML'
            )
            return
        
        # Проверка срока действия кода
        if user.code_expires_at and datetime.now() > user.code_expires_at:
            logger.warning(f"Код {code} истёк для пользователя {user.id}")
            await message.answer(
                "⏰ <b>Срок действия кода истёк</b>\n\n"
                "Код регистрации действителен только 72 часа.\n"
                "Обратитесь к администратору для получения нового кода.",
                parse_mode='HTML'
            )
            return
        
        # Успешная регистрация - обновляем данные пользователя
        user.telegram_id = telegram_id
        user.telegram_username = telegram_username
        user.first_name = first_name
        user.last_name = last_name
        user.registration_code = None  # Очищаем код (одноразовый)
        user.code_expires_at = None
        user.registered_at = datetime.now()
        
        db.commit()
        db.refresh(user)
        
        # Очищаем состояние FSM
        await state.clear()
        
        # Импортируем клавиатуру для клиентов
        from bot.handlers.client_buttons import get_client_keyboard
        
        # Отправляем приветственное сообщение с клавиатурой
        success_message = f"""
✅ <b>Регистрация успешно завершена!</b>

Привет, <b>{user.full_name}</b>!

Вы подключены к системе уведомлений о дедлайнах.

<b>Ваша компания:</b> {user.company_name or 'Не указана'}
<b>ИНН:</b> {user.inn or 'Не указан'}

📋 <b>Доступные команды:</b>
• /list - Показать все ваши дедлайны (30 дней)
• /today - Дедлайны на сегодня
• /week - Дедлайны на неделю
• /next &lt;дни&gt; - Дедлайны на N дней вперёд
• /help - Справка по командам

🔔 Вы будете получать автоматические уведомления о приближающихся дедлайнах.

💡 <b>Используйте кнопки меню ниже для быстрого доступа:</b>
• 📋 Мои дедлайны - текущие сроки
• ❓ Помощь - создать обращение в поддержку

Для управления дедлайнами используйте веб-консоль.
"""
        
        await message.answer(success_message, parse_mode='HTML', reply_markup=get_client_keyboard())
        
        logger.info(f"✅ Пользователь {telegram_id} успешно зарегистрирован как {user.company_name} (ID: {user.id})")
        
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя {telegram_id}: {e}")
        logger.error(f"Детали ошибки:", exc_info=True)  # Добавляем трейсбек
        await message.answer(
            "❌ Произошла ошибка при регистрации.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.",
            parse_mode='HTML'
        )
        db.rollback()
    finally:
        db.close()


async def check_user_registered(telegram_id: int) -> tuple[bool, User]:
    """
    Проверка, зарегистрирован ли пользователь
    
    Args:
        telegram_id: Telegram ID пользователя
        
    Returns:
        tuple: (зарегистрирован, объект пользователя или None)
    """
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(
            User.telegram_id == str(telegram_id),
            User.role == 'client',
            User.is_active == True
        ).first()
        
        return (user is not None, user)
    finally:
        db.close()


# Экспорт
__all__ = ['router', 'start_registration', 'check_user_registered', 'RegistrationStates']
