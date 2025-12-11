# -*- coding: utf-8 -*-
"""
Исключения для Web API клиента
Определяет специфичные ошибки для обработки API запросов
"""


class APIError(Exception):
    """Базовое исключение для всех ошибок API"""
    pass


class TokenRefreshError(APIError):
    """Ошибка обновления JWT токена"""
    pass


class ConnectionError(APIError):
    """Ошибка подключения к API"""
    pass


class NotFoundError(APIError):
    """Ресурс не найден (404)"""
    pass


class ValidationError(APIError):
    """Ошибка валидации запроса (422)"""
    pass


class ServerError(APIError):
    """Ошибка сервера (500+)"""
    pass


class CircuitOpenError(APIError):
    """Circuit breaker открыт - API временно недоступен"""
    pass