"""
Пакет обработчиков команд Telegram бота
"""
from . import common, admin, deadlines, settings, search
from . import client_management, deadline_management, export

# Экспорт всех роутеров
__all__ = [
    'common',
    'admin',
    'deadlines',
    'settings',
    'search',
    'client_management',
    'deadline_management',
    'export'
]