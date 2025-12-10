# -*- coding: utf-8 -*-
"""
Логирующее middleware для Telegram бота
Записывает информацию о входящих сообщениях и ошибках
"""

import time
import logging
import traceback
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Dict, Callable, Awaitable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования входящих сообщений и ошибок
    """

    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка входящего события и логирование
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Входящее событие (сообщение)
            data: Данные события
            
        Returns:
            Any: Результат выполнения обработчика
        """
        start_time = time.time()
        
        try:
            # Логируем входящее сообщение
            if isinstance(event, Message):
                user = event.from_user
                logger.info(
                    f"📥 Входящее сообщение от @{user.username or user.id} "
                    f"(ID: {user.id}): {event.text or '[non-text]'}"
                )
            elif isinstance(event, CallbackQuery):
                user = event.from_user
                logger.info(
                    f"📥 Callback от @{user.username or user.id} "
                    f"(ID: {user.id}): {event.data}"
                )
            
            # Выполняем обработчик
            result = await handler(event, data)
            
            # Логируем успешное выполнение
            execution_time = time.time() - start_time
            if isinstance(event, Message):
                logger.info(
                    f"✅ Сообщение обработано за {execution_time:.3f} секунд"
                )
            elif isinstance(event, CallbackQuery):
                logger.info(
                    f"✅ Callback обработан за {execution_time:.3f} секунд"
                )
                
            return result
            
        except Exception as e:
            # Логируем ошибку с полной трассировкой
            execution_time = time.time() - start_time
            logger.error(
                f"❌ Ошибка обработки сообщения за {execution_time:.3f} секунд: {e}\n"
                f"Трассировка: {traceback.format_exc()}"
            )
            
            # Пытаемся отправить уведомление об ошибке администратору
            try:
                from bot.config import get_bot_config
                config = get_bot_config()
                
                # Получаем бота из данных
                bot = data.get('bot')
                if bot:
                    await bot.send_message(
                        chat_id=config['telegram_admin_id'],
                        text=f"❌ Ошибка в боте: {str(e)}"
                    )
            except Exception as notify_error:
                logger.error(f"❌ Не удалось отправить уведомление об ошибке: {notify_error}")
            
            # Повторно вызываем исключение
            raise


# Экспортируем middleware для использования
__all__ = ['LoggingMiddleware']