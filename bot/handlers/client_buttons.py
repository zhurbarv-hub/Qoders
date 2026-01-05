"""
Обработчики кнопок для клиентов в Telegram боте
Реализованы функции:
1. Кнопка "Помощь" - создание обращения в поддержку
2. Кнопка "Мои дедлайны" - просмотр текущих дедлайнов
"""
import logging
from datetime import date
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session

from backend.models import User
from bot.services import checker

logger = logging.getLogger(__name__)

# Создаём роутер
router = Router()


async def notify_admins_about_support_request(
    support_request,
    client_id: int,
    db_session: Session
):
    """
    Отправка уведомления администраторам о новом обращении клиента
    Отправляет уведомление в группу администраторов (если настроена) или индивидуально каждому админу
    
    Args:
        support_request: Объект SupportRequest из БД
        client_id: ID клиента, создавшего обращение
        db_session: Сессия базы данных
    """
    try:
        from backend.config import settings
        
        # Получаем информацию о клиенте
        client = db_session.query(User).filter(User.id == client_id).first()
        if not client:
            logger.warning(f"Клиент {client_id} не найден для уведомления")
            return
        
        # Формируем текст уведомления
        client_name = client.company_name or client.full_name or "Неизвестный клиент"
        client_inn = client.inn or "Не указан"
        client_telegram = f"@{client.telegram_username}" if client.telegram_username else "Не указан"
        
        notification_text = (
            f"🔔 <b>Новое обращение от клиента!</b>\n\n"
            f"📋 <b>Номер обращения:</b> #{support_request.id}\n"
            f"👤 <b>Клиент:</b> {client_name}\n"
            f"🏢 <b>ИНН:</b> {client_inn}\n"
            f"💬 <b>Telegram:</b> {client_telegram}\n\n"
            f"📌 <b>Тема:</b> {support_request.subject}\n\n"
            f"📝 <b>Сообщение:</b>\n{support_request.message}\n\n"
            f"📞 <b>Контакт:</b> {support_request.contact_phone}\n\n"
            f"⏰ <b>Время создания:</b> {support_request.created_at.strftime('%d.%m.%Y %H:%M')}"
        )
        
        # Создаем бота для отправки уведомлений
        bot = Bot(token=settings.telegram_bot_token)
        
        # Проверяем, настроена ли группа администраторов
        admin_group_chat_id = settings.admin_group_chat_id.strip() if settings.admin_group_chat_id else None
        
        if admin_group_chat_id:
            # Отправка в группу администраторов
            try:
                await bot.send_message(
                    chat_id=admin_group_chat_id,
                    text=notification_text,
                    parse_mode='HTML'
                )
                logger.info(f"✅ Уведомление об обращении #{support_request.id} отправлено в группу администраторов (chat_id: {admin_group_chat_id})")
            except Exception as group_error:
                logger.error(f"❌ Ошибка отправки в группу администраторов: {group_error}")
                logger.warning("⚠️ Переключаемся на индивидуальную отправку администраторам")
                # Если не удалось отправить в группу, отправляем индивидуально
                await _send_to_individual_admins(bot, notification_text, support_request, db_session)
        else:
            # Группа не настроена - отправляем индивидуально каждому администратору
            logger.info("📧 ADMIN_GROUP_CHAT_ID не настроен, отправляем уведомления индивидуально")
            await _send_to_individual_admins(bot, notification_text, support_request, db_session)
        
        # Закрываем сессию бота
        await bot.session.close()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке уведомлений администраторам: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


async def _send_to_individual_admins(
    bot: Bot,
    notification_text: str,
    support_request,
    db_session: Session
):
    """
    Вспомогательная функция для отправки уведомлений индивидуально каждому администратору
    
    Args:
        bot: Экземпляр бота
        notification_text: Текст уведомления
        support_request: Объект обращения
        db_session: Сессия БД
    """
    # Получаем всех администраторов с telegram_id
    admins = db_session.query(User).filter(
        User.role == 'admin',
        User.telegram_id.isnot(None),
        User.is_active.is_(True)
    ).all()
    
    if not admins:
        logger.warning("Нет активных администраторов с Telegram ID для отправки уведомлений")
        return
    
    # Отправляем уведомление каждому администратору
    sent_count = 0
    for admin in admins:
        try:
            await bot.send_message(
                chat_id=int(admin.telegram_id),
                text=notification_text,
                parse_mode='HTML'
            )
            sent_count += 1
            logger.info(f"✅ Уведомление отправлено администратору {admin.full_name} (ID: {admin.telegram_id})")
        except Exception as send_error:
            logger.error(f"❌ Ошибка отправки администратору {admin.full_name}: {send_error}")
    
    logger.info(f"📨 Уведомление об обращении #{support_request.id} отправлено {sent_count}/{len(admins)} администраторам")


# FSM состояния для формы обращения
class SupportRequestStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_text = State()
    waiting_for_phone = State()


# Клавиатура с кнопками для клиента
def get_client_keyboard():
    """Создание клавиатуры с кнопками для клиента"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Мои дедлайны"),
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


@router.message(F.text == "📋 Мои дедлайны")
async def cmd_my_deadlines(
    message: Message,
    user_role: str = 'unknown',
    client_id: int = None,
    db_session: Session = None,
    **kwargs
):
    """
    Обработчик кнопки "Мои дедлайны"
    Отправляет текущие дедлайны клиента (аналогично кнопке в карточке)
    """
    user = message.from_user
    logger.info(f"📋 Кнопка 'Мои дедлайны' от пользователя {user.id}, роль={user_role}")
    
    # Проверка, что это клиент
    if user_role != 'client' or not client_id:
        await message.answer(
            "⚠️ <b>Эта функция доступна только для клиентов</b>\n\n"
            "Пожалуйста, зарегистрируйтесь с помощью кода регистрации.",
            parse_mode='HTML'
        )
        return
    
    try:
        # Получаем данные клиента из БД
        client = db_session.query(User).filter(User.id == client_id).first()
        
        if not client:
            await message.answer("❌ Ошибка: данные клиента не найдены")
            return
        
        # Получаем дедлайны через API/БД
        # Используем модель Deadline из web.app.models.client (с cash_register_id)
        from web.app.models.client import Deadline
        from datetime import date
        
        deadlines = db_session.query(Deadline).filter(
            Deadline.client_id == client_id,
            Deadline.status == 'active'
        ).order_by(Deadline.expiration_date).all()
        
        if not deadlines:
            await message.answer(
                "✅ <b>У вас нет активных дедлайнов!</b>\n\n"
                "Все ваши услуги актуальны.",
                parse_mode='HTML'
            )
            return
        
        # Формируем данные для отправки
        today = date.today()
        deadlines_data = []
        
        for deadline in deadlines:
            days_diff = (deadline.expiration_date - today).days
            
            # Определение статуса
            if days_diff < 0:
                status_color = "expired"
            elif days_diff <= 7:
                status_color = "red"
            elif days_diff <= 14:
                status_color = "yellow"
            else:
                status_color = "green"
            
            # Базовая информация о дедлайне
            deadline_info = {
                'deadline_id': deadline.id,
                'client_name': client.company_name or client.full_name,
                'client_inn': client.inn or 'Не указано',
                'deadline_type_name': deadline.deadline_type.type_name if deadline.deadline_type else 'Неизвестно',
                'expiration_date': deadline.expiration_date,
                'days_remaining': days_diff,
                'status': status_color
            }
            
            # Добавляем информацию о кассе, если дедлайн привязан к кассе
            if deadline.cash_register_id and deadline.cash_register:
                cash_register = deadline.cash_register
                deadline_info['cash_register_model'] = cash_register.model or 'Не указана'
                deadline_info['cash_register_serial'] = cash_register.factory_number or 'Не указан'
                deadline_info['cash_register_name'] = cash_register.register_name or cash_register.model or 'ККТ'
                deadline_info['installation_address'] = cash_register.installation_address
            
            deadlines_data.append(deadline_info)
        
        # Форматируем и отправляем
        from bot.services.formatter import format_deadline_list
        
        title = f"📄 Ваши текущие дедлайны ({len(deadlines_data)})"
        message_text = format_deadline_list(deadlines_data, title=title)
        
        await message.answer(message_text, parse_mode='HTML')
        logger.info(f"✅ Отправлено {len(deadlines_data)} дедлайнов клиенту {client_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении дедлайнов: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await message.answer(
            "⚠️ Произошла ошибка при получении дедлайнов.\n"
            "Пожалуйста, попробуйте позже.",
            parse_mode='HTML'
        )


@router.message(F.text == "❓ Помощь")
async def cmd_support_start(
    message: Message,
    state: FSMContext,
    user_role: str = 'unknown',
    client_id: int = None,
    **kwargs
):
    """
    Обработчик кнопки "Помощь"
    Начало процесса создания обращения в поддержку
    """
    user = message.from_user
    logger.info(f"❓ Кнопка 'Помощь' от пользователя {user.id}, роль={user_role}")
    
    # Проверка, что это клиент
    if user_role != 'client' or not client_id:
        await message.answer(
            "⚠️ <b>Эта функция доступна только для клиентов</b>\n\n"
            "Пожалуйста, зарегистрируйтесь с помощью кода регистрации.",
            parse_mode='HTML'
        )
        return
    
    # Сохраняем client_id в состоянии
    await state.update_data(client_id=client_id)
    
    # Переходим в состояние ожидания темы
    await state.set_state(SupportRequestStates.waiting_for_subject)
    
    await message.answer(
        "📝 <b>Создание обращения в поддержку</b>\n\n"
        "Пожалуйста, укажите <b>тему обращения</b>:\n\n"
        "Например:\n"
        "• Вопрос по продлению договора ОФД\n"
        "• Проблема с кассой\n"
        "• Консультация по замене ФН\n\n"
        "Или отправьте /cancel для отмены",
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(SupportRequestStates.waiting_for_subject)
async def process_subject(message: Message, state: FSMContext):
    """Обработка темы обращения"""
    
    # Проверка на отмену
    if message.text and message.text.lower() in ['/cancel', 'отмена']:
        await state.clear()
        await message.answer(
            "❌ Создание обращения отменено",
            reply_markup=get_client_keyboard()
        )
        return
    
    # Сохраняем тему
    await state.update_data(subject=message.text)
    
    # Переходим к тексту обращения
    await state.set_state(SupportRequestStates.waiting_for_text)
    
    await message.answer(
        "📄 <b>Опишите вашу проблему или вопрос:</b>\n\n"
        "Пожалуйста, укажите детали обращения.\n"
        "Чем подробнее, тем быстрее мы сможем вам помочь.\n\n"
        "Или отправьте /cancel для отмены",
        parse_mode='HTML'
    )


@router.message(SupportRequestStates.waiting_for_text)
async def process_text(message: Message, state: FSMContext):
    """Обработка текста обращения"""
    
    # Проверка на отмену
    if message.text and message.text.lower() in ['/cancel', 'отмена']:
        await state.clear()
        await message.answer(
            "❌ Создание обращения отменено",
            reply_markup=get_client_keyboard()
        )
        return
    
    # Сохраняем текст
    await state.update_data(text=message.text)
    
    # Переходим к телефону
    await state.set_state(SupportRequestStates.waiting_for_phone)
    
    await message.answer(
        "📞 <b>Контакт для обратной связи:</b>\n\n"
        "Укажите ваш телефон для связи.\n"
        "Например: +7 900 123-45-67\n\n"
        "Или отправьте /cancel для отмены",
        parse_mode='HTML'
    )


@router.message(SupportRequestStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, db_session: Session = None, **kwargs):
    """Обработка телефона и создание обращения"""
    
    # Проверка на отмену
    if message.text and message.text.lower() in ['/cancel', 'отмена']:
        await state.clear()
        await message.answer(
            "❌ Создание обращения отменено",
            reply_markup=get_client_keyboard()
        )
        return
    
    # Получаем все данные из состояния
    data = await state.get_data()
    phone = message.text
    
    try:
        # Создаём обращение в БД
        from backend.models import SupportRequest
        from datetime import datetime
        
        support_request = SupportRequest(
            client_id=data['client_id'],
            subject=data['subject'],
            message=data['text'],
            contact_phone=phone,
            status='new',
            created_at=datetime.now()
        )
        
        db_session.add(support_request)
        db_session.commit()
        db_session.refresh(support_request)
        
        logger.info(f"✅ Создано обращение #{support_request.id} от клиента {data['client_id']}")
        
        # Отправляем уведомление администраторам
        try:
            await notify_admins_about_support_request(
                support_request=support_request,
                client_id=data['client_id'],
                db_session=db_session
            )
        except Exception as notify_error:
            logger.error(f"⚠️ Ошибка отправки уведомления администраторам: {notify_error}")
            # Продолжаем работу, даже если уведомление не отправлено
        
        # Очищаем состояние
        await state.clear()
        
        # Отправляем подтверждение
        await message.answer(
            "✅ <b>Обращение успешно создано!</b>\n\n"
            f"📋 <b>Номер обращения:</b> #{support_request.id}\n"
            f"📌 <b>Тема:</b> {data['subject']}\n"
            f"📞 <b>Контакт:</b> {phone}\n\n"
            "Мы свяжемся с вами в ближайшее время.\n"
            "Спасибо за обращение!",
            parse_mode='HTML',
            reply_markup=get_client_keyboard()
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания обращения: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await state.clear()
        await message.answer(
            "⚠️ Произошла ошибка при создании обращения.\n"
            "Пожалуйста, попробуйте позже или свяжитесь с нами по телефону.",
            parse_mode='HTML',
            reply_markup=get_client_keyboard()
        )


# Экспорт роутера
__all__ = ['router', 'get_client_keyboard']
