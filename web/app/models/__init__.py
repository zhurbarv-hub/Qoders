# -*- coding: utf-8 -*-
"""
Модели веб-приложения
"""
from .client import Client, DeadlineType, Deadline, Contact, NotificationLog
from .user import WebUser
from .cash_register import CashRegister
from .ofd_provider import OFDProvider

__all__ = [
    'Client',
    'DeadlineType', 
    'Deadline',
    'Contact',
    'NotificationLog',
    'WebUser',
    'CashRegister',
    'OFDProvider'
]