# -*- coding: utf-8 -*-
"""
Конфигурация веб-приложения
"""
from typing import List


class WebSettings:
    """Настройки веб-интерфейса"""
    
    # Безопасность
    secret_key: str = "your-secret-key-change-in-production-please-make-it-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 часов
    
    # База данных
    database_url: str = "sqlite:///./kkt_system.db"
    
    # Сервер
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS
    cors_origins: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]


# Глобальный экземпляр настроек
settings = WebSettings()