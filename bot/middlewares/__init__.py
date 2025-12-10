"""
Middleware для обработки входящих сообщений
"""
from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.logging import LoggingMiddleware

__all__ = ['AuthMiddleware', 'LoggingMiddleware']