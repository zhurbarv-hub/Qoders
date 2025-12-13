"""
Пакет обработчиков команд Telegram бота
"""
from . import common, admin, deadlines, settings, search, export, registration

# Экспорт всех роутеров
__all__ = [
    'common',
    'admin',
    'deadlines',
    'settings',
    'search',
    'export',
    'registration'
]