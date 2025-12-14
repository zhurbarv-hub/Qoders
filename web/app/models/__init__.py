# -*- coding: utf-8 -*-
"""
Модели веб-приложения
"""
from .client import DeadlineType, Deadline, NotificationLog
from .user import WebUser, User
from .cash_register import CashRegister
from .ofd_provider import OFDProvider

__all__ = [
    'DeadlineType', 
    'Deadline',
    'NotificationLog',
    'WebUser',
    'User',
    'CashRegister',
    'OFDProvider'
]