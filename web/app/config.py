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
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 часов
    
    # База данных
    database_url: str = "sqlite:///database/kkt_services.db"
    
    # Сервер
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",  # Vite dev server (CoreUI admin)
        "http://127.0.0.1:3000"
    ]
    
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