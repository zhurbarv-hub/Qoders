"""
Административные команды Telegram бота
Доступны только администратору
ОБНОВЛЕНО: добавлена команда /health, /status использует Web API
"""
import logging
import time
from datetime import datetime
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from bot.services.notifier import process_deadline_notifications
from bot.services.formatter import format_api_statistics, format_health_status
from bot.services import checker
from backend.config import settings
from backend.models import User

logger = logging.getLogger(__name__)

# Создаём роутер для административных команд
router = Router()


def find_client_by_name(db_session: Session, search_query: str):
    """
    Поиск клиента по названию компании или части названия
    
    Args:
        db_session: Сессия базы данных
        search_query: Строка поиска
        
    Returns:
        Список найденных клиентов
    """
    search_pattern = f"%{search_query}%"
    
    clients = db_session.query(User).filter(
        User.role == 'client',
        User.is_active == True,
        User.company_name.ilike(search_pattern)
    ).all()
    
    return clients


@router.message(Command('check'))
async def cmd_check(
    message: Message,
    bot: Bot,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    Обработчик команды /check
    Принудительная проверка дедлайнов и отправка уведомлений
    
    Args:
        message: Сообщение от пользователя
        bot: Экземпляр бота
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
    # Проверка прав администратора
    if not is_admin:
        logger.warning(f"⛔ Попытка /check от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"🔍 /check от администратора {user.id}")
    
    # Отправляем сообщение о начале проверки
    status_msg = await message.answer(
        "🔄 <b>Запуск проверки дедлайнов...</b>\n\n"
        "Это может занять несколько секунд.",
        parse_mode='HTML'
    )
    
    try:
        # Получаем дни для проверки из конфигурации
        days_list = settings.notification_days_list
        
        total_stats = {
            'checked': 0,
            'sent': 0,
            'failed': 0,
            'skipped': 0
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
        
        # Определяем источник данных
        api_client = checker._api_client
        data_source = "🔌 Web API" if api_client else "💾 База данных"
        
        # Формируем отчёт
        report = f"""
✅ <b>Проверка завершена</b>

📊 <b>Результаты:</b>
• Проверено дедлайнов: <b>{total_stats['checked']}</b>
• Отправлено уведомлений: <b>{total_stats['sent']}</b>
• Пропущено (дубликаты): <b>{total_stats['skipped']}</b>
• Ошибок отправки: <b>{total_stats['failed']}</b>

📡 <b>Источник данных:</b> {data_source}

⏰ Автоматическая проверка: <b>{settings.notification_check_time}</b> ({settings.notification_timezone})
📅 Дни уведомлений: <b>{', '.join(map(str, days_list))}</b>
""".strip()
        
        await status_msg.edit_text(report, parse_mode='HTML')
        logger.info(f"✅ Проверка завершена: {total_stats}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении /check: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при проверке</b>\n\n"
            f"<code>{str(e)[:200]}</code>\n\n"
            f"Проверьте логи для подробностей.",
            parse_mode='HTML'
        )


@router.message(Command('status'))
async def cmd_status(
    message: Message,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    Обработчик команды /status
    Показывает статистику системы
    ОБНОВЛЕНО: использует Web API для получения статистики
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
    # Проверка прав администратора
    if not is_admin:
        logger.warning(f"⛔ Попытка /status от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"📊 /status от администратора {user.id}")
    
    # Показываем индикатор загрузки
    status_msg = await message.answer("⏳ Загрузка статистики...", parse_mode='HTML')
    
    try:
        # Получаем API клиент из checker service
        api_client = checker._api_client
        
        if api_client:
            # Попытка получить статистику через Web API
            try:
                start_time = time.time()
                stats = await api_client.get_dashboard_stats()
                response_time = int((time.time() - start_time) * 1000)  # в миллисекундах
                
                # Добавляем время ответа API
                stats['api_response_time'] = response_time
                stats['data_source'] = 'api'
                
                # Форматируем статистику из API
                status_text = format_api_statistics(stats)
                
                await status_msg.edit_text(status_text, parse_mode='HTML')
                logger.info(f"✅ Статистика отправлена (источник: Web API, {response_time}ms)")
                return
                
            except Exception as api_error:
                logger.warning(f"⚠️ Web API недоступен для /status, используем fallback: {api_error}")
        
        # Fallback: получаем статистику из БД напрямую
        from backend.models import User, Deadline
        from datetime import date
        
        stats = {}
        
        # Количество активных клиентов
        stats['active_clients_count'] = db_session.query(User).filter(
            User.role == 'client',
            User.is_active == True
        ).count()
        
        stats['total_clients_count'] = db_session.query(User).filter(
            User.role == 'client'
        ).count()
        
        # Количество дедлайнов по статусам
        all_deadlines = db_session.query(Deadline).filter(
            Deadline.status == 'active'
        ).all()
        
        stats['active_deadlines_count'] = len(all_deadlines)
        stats['total_deadlines_count'] = db_session.query(Deadline).count()
        
        # Подсчёт по статусам
        today = date.today()
        green_count = 0
        yellow_count = 0
        red_count = 0
        expired_count = 0
        
        for deadline in all_deadlines:
            days_remaining = (deadline.expiration_date - today).days
            
            if days_remaining < 0:
                expired_count += 1
            elif days_remaining < 7:
                red_count += 1
            elif days_remaining < 14:
                yellow_count += 1
            else:
                green_count += 1
        
        stats['status_green'] = green_count
        stats['status_yellow'] = yellow_count
        stats['status_red'] = red_count
        stats['status_expired'] = expired_count
        stats['data_source'] = 'database'
        
        # Форматируем статистику
        status_text = format_api_statistics(stats)
        
        await status_msg.edit_text(status_text, parse_mode='HTML')
        logger.info(f"✅ Статистика отправлена (источник: БД fallback)")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /status: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при получении статистики</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


@router.message(Command('health'))
async def cmd_health(
    message: Message,
    user_role: str = 'unknown',
    **kwargs
):
    """
    НОВАЯ КОМАНДА: /health
    Проверка здоровья Web API и статуса подключения
    Доступна только администратору
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
    # Проверка прав администратора
    if not is_admin:
        logger.warning(f"⛔ Попытка /health от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"🏥 /health от администратора {user.id}")
    
    # Показываем индикатор проверки
    status_msg = await message.answer("🔍 Проверка Web API...", parse_mode='HTML')
    
    try:
        # Получаем API клиент из checker service
        api_client = checker._api_client
        
        if not api_client:
            await status_msg.edit_text(
                "⚠️ <b>Web API клиент не инициализирован</b>\n\n"
                "Бот работает в режиме прямого доступа к базе данных.",
                parse_mode='HTML'
            )
            return
        
        # Проверяем статус токена
        token_manager = api_client.token_manager
        token_valid = token_manager._is_token_valid() if hasattr(token_manager, '_is_token_valid') else False
        
        health_data = {
            'api_url': settings.web_api_base_url,
            'token_valid': token_valid,
            'api_available': False,
            'response_time': None,
            'error': None
        }
        
        # Проверяем доступность API
        try:
            start_time = time.time()
            stats = await api_client.get_dashboard_stats()
            response_time = int((time.time() - start_time) * 1000)
            
            health_data['api_available'] = True
            health_data['response_time'] = response_time
            health_data['stats'] = stats
            
        except Exception as api_error:
            health_data['error'] = str(api_error)
        
        # Форматируем результат проверки
        health_text = format_health_status(health_data)
        
        await status_msg.edit_text(health_text, parse_mode='HTML')
        logger.info(f"✅ Health check завершён: API {'доступен' if health_data['api_available'] else 'недоступен'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /health: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при проверке здоровья</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


@router.message(Command('filter'))
async def cmd_filter(
    message: Message,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    НОВАЯ КОМАНДА: /filter <user_id>
    Фильтрация дедлайнов по конкретному клиенту
    Доступна администраторам и менеджерам
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_authorized = (user_role in ['admin', 'manager'])
    
    # Проверка прав доступа
    if not is_authorized:
        logger.warning(f"⛔ Попытка /filter от неавторизованного: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администраторам и менеджерам.",
            parse_mode='HTML'
        )
        return
    
    # Разбираем аргументы команды
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "ℹ️ <b>Использование команды /filter</b>\n\n"
            "<code>/filter &lt;user_id или название&gt;</code>\n\n"
            "Примеры:\n"
            "• /filter 5 - дедлайны клиента с ID 5\n"
            "• /filter all - все активные дедлайны\n"
            "• /filter Петров - поиск по названию компании\n"
            "• /filter ООО - поиск по части названия",
            parse_mode='HTML'
        )
        return
    
    filter_param = args[1].strip()
    
    logger.info(f"🔍 /filter от {user_role} {user.id}: параметр='{filter_param}'")
    
    status_msg = await message.answer("🔄 Загрузка дедлайнов...", parse_mode='HTML')
    
    try:
        from backend.models import User, Deadline, DeadlineType
        from datetime import date
        
        # Строим базовый запрос
        query = db_session.query(
            Deadline.id.label('deadline_id'),
            User.company_name.label('client_name'),
            User.inn.label('client_inn'),
            DeadlineType.type_name.label('deadline_type_name'),
            Deadline.expiration_date.label('expiration_date'),
            User.id.label('user_id')
        ).join(
            User, Deadline.user_id == User.id
        ).join(
            DeadlineType, Deadline.deadline_type_id == DeadlineType.id
        ).filter(
            Deadline.status == 'active',
            User.is_active == True,
            User.role == 'client'
        )
        
        # Применяем фильтр
        if filter_param.lower() != 'all':
            # Пробуем найти по ID
            try:
                user_id = int(filter_param)
                query = query.filter(User.id == user_id)
                
                # Проверяем существование клиента
                client = db_session.query(User).filter(
                    User.id == user_id,
                    User.role == 'client'
                ).first()
                
                if not client:
                    await status_msg.edit_text(
                        f"❌ <b>Клиент не найден</b>\n\n"
                        f"Клиент с ID {user_id} не существует.",
                        parse_mode='HTML'
                    )
                    return
                    
                filter_title = f"Дедлайны клиента: {client.company_name}"
                
            except ValueError:
                # Не число - ищем по названию компании
                found_clients = find_client_by_name(db_session, filter_param)
                
                if not found_clients:
                    await status_msg.edit_text(
                        f"❌ <b>Клиенты не найдены</b>\n\n"
                        f"По запросу '{filter_param}' клиенты не найдены.\n\n"
                        f"Попробуйте:\n"
                        f"• Использовать часть названия\n"
                        f"• Проверить правильность написания\n"
                        f"• Использовать /search для поиска клиентов",
                        parse_mode='HTML'
                    )
                    return
                
                # Если найден один клиент - фильтруем по нему
                if len(found_clients) == 1:
                    client = found_clients[0]
                    query = query.filter(User.id == client.id)
                    filter_title = f"Дедлайны клиента: {client.company_name}"
                    
                # Если найдено несколько - показываем список для выбора
                else:
                    clients_list = "\n".join([
                        f"• ID {c.id}: {c.company_name} (ИНН: {c.inn or 'не указан'})"
                        for c in found_clients[:10]  # Показываем первые 10
                    ])
                    
                    more_text = ""
                    if len(found_clients) > 10:
                        more_text = f"\n\n... и ещё {len(found_clients) - 10} клиентов"
                    
                    await status_msg.edit_text(
                        f"🔍 <b>Найдено клиентов: {len(found_clients)}</b>\n\n"
                        f"{clients_list}{more_text}\n\n"
                        f"Используйте:\n"
                        f"<code>/filter &lt;ID&gt;</code> - для фильтрации по конкретному клиенту\n"
                        f"Или уточните запрос для более точного поиска.",
                        parse_mode='HTML'
                    )
                    return
        else:
            filter_title = "Все активные дедлайны"
        
        # Выполняем запрос
        results = query.order_by(Deadline.expiration_date).all()
        
        if not results:
            await status_msg.edit_text(
                f"📭 <b>{filter_title}</b>\n\n"
                "Дедлайны не найдены.",
                parse_mode='HTML'
            )
            return
        
        # Форматируем результаты
        today = date.today()
        deadlines = []
        
        for row in results:
            days_remaining = (row.expiration_date - today).days
            
            # Определяем статус
            if days_remaining < 0:
                status = 'expired'
            elif days_remaining < 7:
                status = 'red'
            elif days_remaining < 14:
                status = 'yellow'
            else:
                status = 'green'
            
            deadlines.append({
                'deadline_id': row.deadline_id,
                'client_name': row.client_name or 'Неизвестно',
                'client_inn': row.client_inn or 'Неизвестно',
                'deadline_type_name': row.deadline_type_name,
                'expiration_date': row.expiration_date,
                'days_remaining': days_remaining,
                'status': status,
                'user_id': row.user_id
            })
        
        # Форматируем список
        from bot.services.formatter import format_deadline_list
        message_text = format_deadline_list(deadlines, title=f"🔍 {filter_title}")
        message_text += f"\n\n📊 <b>Всего:</b> {len(deadlines)} дедлайнов"
        
        await status_msg.edit_text(message_text, parse_mode='HTML')
        logger.info(f"✅ Фильтр выполнен: найдено {len(deadlines)} дедлайнов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /filter: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при фильтрации</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


@router.message(Command('client'))
async def cmd_client(
    message: Message,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    НОВАЯ КОМАНДА: /client <user_id или название>
    Показать карточку клиента с контактами и дедлайнами
    Поддерживает поиск по ID или названию компании
    Доступна администраторам и менеджерам
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_authorized = (user_role in ['admin', 'manager'])
    
    # Проверка прав доступа
    if not is_authorized:
        logger.warning(f"⛔ Попытка /client от неавторизованного: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администраторам и менеджерам.",
            parse_mode='HTML'
        )
        return
    
    # Разбираем аргументы команды
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "ℹ️ <b>Использование команды /client</b>\n\n"
            "<code>/client &lt;user_id или название&gt;</code>\n\n"
            "Примеры:\n"
            "• /client 5 - карточка клиента с ID 5\n"
            "• /client Петров - поиск по названию\n"
            "• /client ИП - поиск по части названия",
            parse_mode='HTML'
        )
        return
    
    search_param = args[1].strip()
    
    # Пробуем найти по ID
    client = None
    try:
        user_id = int(search_param)
        logger.info(f"👤 /client от {user_role} {user.id}: user_id={user_id}")
    except ValueError:
        # Не число - ищем по названию
        logger.info(f"👤 /client от {user_role} {user.id}: поиск='{search_param}'")
        
        found_clients = find_client_by_name(db_session, search_param)
        
        if not found_clients:
            await message.answer(
                f"❌ <b>Клиенты не найдены</b>\n\n"
                f"По запросу '{search_param}' клиенты не найдены.\n\n"
                f"Попробуйте:\n"
                f"• Использовать часть названия\n"
                f"• Проверить правильность написания\n"
                f"• Использовать /search для поиска",
                parse_mode='HTML'
            )
            return
        
        # Если найдено несколько - показываем список
        if len(found_clients) > 1:
            clients_list = "\n".join([
                f"• /client {c.id} - {c.company_name} (ИНН: {c.inn or 'не указан'})"
                for c in found_clients[:10]
            ])
            
            more_text = ""
            if len(found_clients) > 10:
                more_text = f"\n\n... и ещё {len(found_clients) - 10} клиентов"
            
            await message.answer(
                f"🔍 <b>Найдено клиентов: {len(found_clients)}</b>\n\n"
                f"{clients_list}{more_text}\n\n"
                f"Выберите клиента, нажав на команду выше,\n"
                f"или уточните запрос для более точного поиска.",
                parse_mode='HTML'
            )
            return
        
        # Найден один клиент
        client = found_clients[0]
        user_id = client.id
    
    status_msg = await message.answer("🔄 Загрузка данных клиента...", parse_mode='HTML')
    
    try:
        from backend.models import User, Deadline, DeadlineType
        from datetime import date
        
        # Получаем данные клиента (если ещё не нашли по названию)
        if not client:
            client = db_session.query(User).filter(
                User.id == user_id,
                User.role == 'client'
            ).first()
        
        if not client:
            await status_msg.edit_text(
                f"❌ <b>Клиент не найден</b>\n\n"
                f"Клиент с ID {user_id} не существует.",
                parse_mode='HTML'
            )
            return
        
        # Формируем карточку клиента
        card_text = f"👤 <b>Карточка клиента</b>\n\n"
        
        # Основная информация
        card_text += f"<b>ID:</b> {client.id}\n"
        card_text += f"<b>Компания:</b> {client.company_name or 'Не указано'}\n"
        card_text += f"<b>ИНН:</b> {client.inn or 'Не указано'}\n"
        card_text += f"<b>Контактное лицо:</b> {client.full_name}\n"
        
        # Контактные данные
        card_text += f"\n📞 <b>Контакты:</b>\n"
        card_text += f"<b>Email:</b> {client.email}\n"
        if client.phone:
            card_text += f"<b>Телефон:</b> {client.phone}\n"
        if client.address:
            card_text += f"<b>Адрес:</b> {client.address}\n"
        
        # Telegram
        card_text += f"\n📱 <b>Telegram:</b>\n"
        if client.telegram_id:
            card_text += f"<b>ID:</b> {client.telegram_id}\n"
            if client.telegram_username:
                card_text += f"<b>Username:</b> @{client.telegram_username}\n"
            card_text += f"<b>Уведомления:</b> {'✅ Включены' if client.notifications_enabled else '❌ Отключены'}\n"
        else:
            card_text += "⚠️ Не привязан к Telegram\n"
            if client.registration_code and client.is_code_valid:
                card_text += f"<b>Код регистрации:</b> <code>{client.registration_code}</code>\n"
                expires = client.code_expires_at.strftime('%d.%m.%Y %H:%M') if client.code_expires_at else 'Неизвестно'
                card_text += f"<b>Действителен до:</b> {expires}\n"
        
        # Статистика по дедлайнам
        card_text += f"\n📊 <b>Дедлайны:</b>\n"
        
        deadlines = db_session.query(Deadline).filter(
            Deadline.user_id == user_id,
            Deadline.status == 'active'
        ).all()
        
        if deadlines:
            today = date.today()
            green_count = 0
            yellow_count = 0
            red_count = 0
            expired_count = 0
            
            for deadline in deadlines:
                days_remaining = (deadline.expiration_date - today).days
                if days_remaining < 0:
                    expired_count += 1
                elif days_remaining < 7:
                    red_count += 1
                elif days_remaining < 14:
                    yellow_count += 1
                else:
                    green_count += 1
            
            card_text += f"<b>Всего активных:</b> {len(deadlines)}\n"
            if green_count > 0:
                card_text += f"   🟢 Безопасно (&gt;14 дней): {green_count}\n"
            if yellow_count > 0:
                card_text += f"   🟡 Внимание (7-14 дней): {yellow_count}\n"
            if red_count > 0:
                card_text += f"   🔴 Критично (&lt;7 дней): {red_count}\n"
            if expired_count > 0:
                card_text += f"   ❌ Просроченные: {expired_count}\n"
        else:
            card_text += "Нет активных дедлайнов\n"
        
        # Статус и метаданные
        card_text += f"\n⚙️ <b>Статус:</b>\n"
        card_text += f"<b>Активен:</b> {'✅ Да' if client.is_active else '❌ Нет'}\n"
        if client.registered_at:
            reg_date = client.registered_at.strftime('%d.%m.%Y %H:%M')
            card_text += f"<b>Зарегистрирован:</b> {reg_date}\n"
        if client.last_interaction:
            last_int = client.last_interaction.strftime('%d.%m.%Y %H:%M')
            card_text += f"<b>Последняя активность:</b> {last_int}\n"
        
        if client.notes:
            card_text += f"\n📝 <b>Заметки:</b>\n{client.notes}\n"
        
        # Подсказка для просмотра дедлайнов
        card_text += f"\n💡 <i>Используйте /filter {user_id} для просмотра всех дедлайнов</i>"
        
        await status_msg.edit_text(card_text, parse_mode='HTML')
        logger.info(f"✅ Карточка клиента {user_id} отправлена")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /client: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при загрузке карточки</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


@router.message(Command('notify'))
async def cmd_notify(
    message: Message,
    bot: Bot,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    НОВАЯ КОМАНДА: /notify <user_id> <deadline_id>
    Принудительно отправить уведомление о дедлайне клиенту
    Доступна только администраторам
    
    Args:
        message: Сообщение от пользователя
        bot: Экземпляр бота
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_admin = (user_role == 'admin')
    
    # Проверка прав администратора
    if not is_admin:
        logger.warning(f"⛔ Попытка /notify от не-админа: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администратору.",
            parse_mode='HTML'
        )
        return
    
    # Разбираем аргументы команды
    args = message.text.split()
    if len(args) < 3:
        await message.answer(
            "ℹ️ <b>Использование команды /notify</b>\n\n"
            "<code>/notify &lt;user_id&gt; &lt;deadline_id&gt;</code>\n\n"
            "Пример: /notify 5 42",
            parse_mode='HTML'
        )
        return
    
    try:
        user_id = int(args[1].strip())
        deadline_id = int(args[2].strip())
    except ValueError:
        await message.answer(
            "❌ <b>Некорректные параметры</b>\n\n"
            "ID клиента и дедлайна должны быть числами.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"📨 /notify от администратора {user.id}: user_id={user_id}, deadline_id={deadline_id}")
    
    status_msg = await message.answer("🔄 Отправка уведомления...", parse_mode='HTML')
    
    try:
        from backend.models import User, Deadline, DeadlineType
        from datetime import date
        from bot.services.notifier import send_notification, log_notification
        from bot.services.formatter import format_deadline_notification
        
        # Проверяем существование клиента
        client = db_session.query(User).filter(
            User.id == user_id,
            User.role == 'client'
        ).first()
        
        if not client:
            await status_msg.edit_text(
                f"❌ <b>Клиент не найден</b>\n\n"
                f"Клиент с ID {user_id} не существует.",
                parse_mode='HTML'
            )
            return
        
        # Проверяем наличие Telegram ID
        if not client.telegram_id:
            await status_msg.edit_text(
                f"❌ <b>Невозможно отправить уведомление</b>\n\n"
                f"Клиент {client.company_name} не привязан к Telegram.\n"
                f"{'Код регистрации: <code>' + client.registration_code + '</code>' if client.registration_code and client.is_code_valid else 'Требуется создание нового кода регистрации.'}",
                parse_mode='HTML'
            )
            return
        
        # Проверяем существование дедлайна
        deadline = db_session.query(Deadline).join(
            DeadlineType, Deadline.deadline_type_id == DeadlineType.id
        ).filter(
            Deadline.id == deadline_id,
            Deadline.user_id == user_id,
            Deadline.status == 'active'
        ).first()
        
        if not deadline:
            await status_msg.edit_text(
                f"❌ <b>Дедлайн не найден</b>\n\n"
                f"Активный дедлайн с ID {deadline_id} для клиента {client.company_name} не существует.",
                parse_mode='HTML'
            )
            return
        
        # Формируем данные для уведомления
        today = date.today()
        days_remaining = (deadline.expiration_date - today).days
        
        if days_remaining < 0:
            status = 'expired'
        elif days_remaining < 7:
            status = 'red'
        elif days_remaining < 14:
            status = 'yellow'
        else:
            status = 'green'
        
        deadline_data = {
            'deadline_id': deadline.id,
            'client_name': client.company_name or client.full_name,
            'client_inn': client.inn or 'Не указано',
            'deadline_type_name': deadline.deadline_type.type_name,
            'expiration_date': deadline.expiration_date,
            'days_remaining': days_remaining,
            'status': status
        }
        
        # Форматируем сообщение
        notification_message = format_deadline_notification(deadline_data, days_remaining)
        notification_message += f"\n\n⚡ <i>Ручное уведомление от администратора</i>"
        
        # Отправляем уведомление
        success = await send_notification(bot, int(client.telegram_id), notification_message)
        
        if success:
            # Записываем в лог
            log_notification(
                deadline_id=deadline.id,
                recipient_id=client.telegram_id,
                days=days_remaining,
                status='sent',
                error=None
            )
            
            await status_msg.edit_text(
                f"✅ <b>Уведомление отправлено</b>\n\n"
                f"<b>Клиент:</b> {client.company_name}\n"
                f"<b>Telegram:</b> @{client.telegram_username or client.telegram_id}\n"
                f"<b>Дедлайн:</b> {deadline.deadline_type.type_name}\n"
                f"<b>Истекает:</b> {deadline.expiration_date.strftime('%d.%m.%Y')} ({days_remaining} дней)",
                parse_mode='HTML'
            )
            logger.info(f"✅ Ручное уведомление отправлено: deadline_id={deadline_id}, user_id={user_id}")
        else:
            # Записываем ошибку в лог
            log_notification(
                deadline_id=deadline.id,
                recipient_id=client.telegram_id,
                days=days_remaining,
                status='failed',
                error='Manual notification failed'
            )
            
            await status_msg.edit_text(
                f"❌ <b>Не удалось отправить уведомление</b>\n\n"
                f"Возможные причины:\n"
                f"• Пользователь заблокировал бота\n"
                f"• Telegram ID неверен\n"
                f"• Проблемы с подключением",
                parse_mode='HTML'
            )
            logger.error(f"❌ Не удалось отправить ручное уведомление: deadline_id={deadline_id}, user_id={user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /notify: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при отправке уведомления</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


@router.message(Command('stats'))
async def cmd_stats(
    message: Message,
    user_role: str = 'unknown',
    db_session: Session = None,
    **kwargs
):
    """
    НОВАЯ КОМАНДА: /stats
    Показать расширенную статистику системы
    Доступна администраторам и менеджерам
    
    Args:
        message: Сообщение от пользователя
        user_role: Роль пользователя из middleware
        db_session: Сессия базы данных
    """
    user = message.from_user
    is_authorized = (user_role in ['admin', 'manager'])
    
    # Проверка прав доступа
    if not is_authorized:
        logger.warning(f"⛔ Попытка /stats от неавторизованного: user_id={user.id}, роль={user_role}")
        await message.answer(
            "❌ <b>Доступ запрещён</b>\n\n"
            "Эта команда доступна только администраторам и менеджерам.",
            parse_mode='HTML'
        )
        return
    
    logger.info(f"📈 /stats от {user_role} {user.id}")
    
    status_msg = await message.answer("🔄 Сбор статистики...", parse_mode='HTML')
    
    try:
        from backend.models import User, Deadline, NotificationLog
        from datetime import date, timedelta
        from sqlalchemy import func
        
        stats_text = "<b>📊 Статистика системы</b>\n\n"
        
        # Клиенты
        stats_text += "👥 <b>Клиенты:</b>\n"
        total_clients = db_session.query(User).filter(User.role == 'client').count()
        active_clients = db_session.query(User).filter(
            User.role == 'client',
            User.is_active == True
        ).count()
        telegram_connected = db_session.query(User).filter(
            User.role == 'client',
            User.telegram_id.isnot(None)
        ).count()
        
        stats_text += f"   Всего: <b>{total_clients}</b>\n"
        stats_text += f"   Активные: <b>{active_clients}</b>\n"
        stats_text += f"   Привязаны к Telegram: <b>{telegram_connected}</b> ({int(telegram_connected / max(total_clients, 1) * 100)}%)\n\n"
        
        # Дедлайны
        stats_text += "📅 <b>Дедлайны:</b>\n"
        total_deadlines = db_session.query(Deadline).count()
        active_deadlines = db_session.query(Deadline).filter(
            Deadline.status == 'active'
        ).count()
        
        stats_text += f"   Всего: <b>{total_deadlines}</b>\n"
        stats_text += f"   Активные: <b>{active_deadlines}</b>\n\n"
        
        # Статусы дедлайнов
        stats_text += "🚦 <b>Статусы активных дедлайнов:</b>\n"
        
        active_deadlines_list = db_session.query(Deadline).filter(
            Deadline.status == 'active'
        ).all()
        
        today = date.today()
        green_count = 0
        yellow_count = 0
        red_count = 0
        expired_count = 0
        
        for deadline in active_deadlines_list:
            days_remaining = (deadline.expiration_date - today).days
            if days_remaining < 0:
                expired_count += 1
            elif days_remaining < 7:
                red_count += 1
            elif days_remaining < 14:
                yellow_count += 1
            else:
                green_count += 1
        
        stats_text += f"   🟢 Безопасно (&gt;14 дней): <b>{green_count}</b>\n"
        stats_text += f"   🟡 Внимание (7-14 дней): <b>{yellow_count}</b>\n"
        stats_text += f"   🔴 Критично (&lt;7 дней): <b>{red_count}</b>\n"
        stats_text += f"   ❌ Просроченные: <b>{expired_count}</b>\n\n"
        
        # Уведомления за последние 30 дней
        stats_text += "📬 <b>Уведомления (за 30 дней):</b>\n"
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        total_notifications = db_session.query(NotificationLog).filter(
            NotificationLog.sent_at >= thirty_days_ago
        ).count()
        
        sent_notifications = db_session.query(NotificationLog).filter(
            NotificationLog.sent_at >= thirty_days_ago,
            NotificationLog.status == 'sent'
        ).count()
        
        failed_notifications = db_session.query(NotificationLog).filter(
            NotificationLog.sent_at >= thirty_days_ago,
            NotificationLog.status == 'failed'
        ).count()
        
        stats_text += f"   Всего отправлено: <b>{total_notifications}</b>\n"
        stats_text += f"   Успешно: <b>{sent_notifications}</b> ({int(sent_notifications / max(total_notifications, 1) * 100)}%)\n"
        stats_text += f"   Ошибки: <b>{failed_notifications}</b>\n\n"
        
        # Ближайшие дедлайны (7 дней)
        stats_text += "⏰ <b>Ближайшие дедлайны (7 дней):</b>\n"
        
        upcoming_date = today + timedelta(days=7)
        upcoming_deadlines = db_session.query(Deadline).filter(
            Deadline.status == 'active',
            Deadline.expiration_date >= today,
            Deadline.expiration_date <= upcoming_date
        ).count()
        
        stats_text += f"   Истекают в ближайшие 7 дней: <b>{upcoming_deadlines}</b>\n\n"
        
        # Настройки системы
        stats_text += "⚙️ <b>Настройки:</b>\n"
        stats_text += f"   Проверка дедлайнов: <b>{settings.notification_check_time}</b>\n"
        stats_text += f"   Дни уведомлений: <b>{', '.join(map(str, settings.notification_days_list))}</b>\n"
        stats_text += f"   Часовой пояс: <b>{settings.notification_timezone}</b>\n\n"
        
        # Временная метка
        timestamp = datetime.now().strftime('%d.%m.%Y %H:%M')
        stats_text += f"🕒 <b>Обновлено:</b> {timestamp}"
        
        await status_msg.edit_text(stats_text, parse_mode='HTML')
        logger.info(f"✅ Статистика отправлена")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при /stats: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        await status_msg.edit_text(
            f"❌ <b>Ошибка при сборе статистики</b>\n\n"
            f"<code>{str(e)[:200]}</code>",
            parse_mode='HTML'
        )


# Экспорт роутера
__all__ = ['router']