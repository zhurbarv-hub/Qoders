# -*- coding: utf-8 -*-
"""
Конфигурация веб-приложения
"""
from typing import List
import os
from pathlib import Path


class WebSettings:
    """Настройки веб-интерфейса"""
    
    # Безопасность
    secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-please-make-it-long-and-random")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("JWT_EXPIRATION_HOURS", "8")) * 60  # Конвертируем часы в минуты
    
    # База данных
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///database/kkt_services.db")
    
    # Сервер
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS - читаем из .env
    _cors_origins_str: str = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
    cors_origins: List[str] = [origin.strip() for origin in _cors_origins_str.split(',')]
    
    # SMTP настройки для отправки email
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "noreply@company.com")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "KKT System")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "noreply@company.com")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # Базовый URL веб-интерфейса (для ссылок активации)
    web_base_url: str = os.getenv("WEB_BASE_URL", "http://localhost:8000")


# Глобальный экземпляр настроек
settings = WebSettings()