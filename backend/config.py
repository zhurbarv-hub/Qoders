# -*- coding: utf-8 -*-
"""
Модуль конфигурации приложения
Использует Pydantic Settings для валидации и управления переменными окружения
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения из переменных окружения
    Автоматически загружает из .env файла
    """
    
    # ============================================
    # Database Configuration
    # ============================================
    database_path: str = Field(
        default="database/kkt_services.db",
        description="Путь к файлу базы данных SQLite"
    )
    
    # ============================================
    # JWT Configuration
    # ============================================
    jwt_secret_key: str = Field(
        description="Секретный ключ для подписи JWT токенов (минимум 32 символа)"
    )
    
    jwt_algorithm: str = Field(
        default="HS256",
        description="Алгоритм шифрования JWT"
    )
    
    jwt_expiration_hours: int = Field(
        default=24,
        description="Срок действия JWT токена (в часах)"
    )
    
    # ============================================
    # Telegram Bot Configuration
    # ============================================
    telegram_bot_token: str = Field(
        description="Токен Telegram бота от @BotFather"
    )
    
    telegram_admin_ids: str = Field(
        default="",
        description="Telegram ID администраторов (через запятую)"
    )
    
    # ============================================
    # Notification Settings
    # ============================================
    notification_time: str = Field(
        default="02:00",
        description="Время ежедневной проверки сроков (формат HH:MM) - deprecated"
    )
    
    notification_check_time: str = Field(
        default="09:00",
        description="Время ежедневной проверки дедлайнов (формат HH:MM)"
    )
    
    notification_timezone: str = Field(
        default="UTC",
        description="Часовой пояс для планировщика"
    )
    
    notification_days: str = Field(
        default="14,7,3",
        description="За сколько дней до истечения отправлять уведомления (через запятую)"
    )
    
    notification_retry_attempts: int = Field(
        default=3,
        description="Количество попыток повтора при ошибке отправки"
    )
    
    notification_retry_delay: int = Field(
        default=300,
        description="Задержка между попытками отправки (секунды)"
    )
    
    alert_threshold_days: int = Field(
        default=14,
        description="За сколько дней до истечения отправлять уведомления - deprecated"
    )
    
    # ============================================
    # API Server Configuration
    # ============================================
    api_host: str = Field(
        default="0.0.0.0",
        description="Хост API сервера"
    )
    api_port: int = Field(
        default=8000,
        description="Порт API сервера"
    )
    api_reload: bool = Field(
        default=True,
        description="Автоматическая перезагрузка при изменении кода (только для разработки)"
    )
    
    # ============================================
    # Logging Configuration
    # ============================================
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file: str = Field(
        default="logs/application.log",
        description="Путь к файлу логов"
    )
    
    # ============================================
    # CORS Settings
    # ============================================
    cors_origins: str = Field(
        default="http://localhost:8000",
        description="Разрешённые источники для CORS (разделённые запятой)"
    )
    
    # ============================================
    # Web API Integration for Bot
    # ============================================
    web_api_base_url: str = Field(
        default="http://localhost:8000",
        description="URL Web API для подключения бота"
    )
    
    web_api_timeout: int = Field(
        default=30,
        description="Таймаут запросов к API (секунды)"
    )
    
    bot_api_username: str = Field(
        default="admin",
        description="Имя пользователя бота для аутентификации в Web API"
    )
    
    bot_api_password: str = Field(
        default="admin",
        description="Пароль бота для аутентификации в Web API"
    )
    
    bot_token_refresh_interval: int = Field(
        default=3600,
        description="Интервал обновления JWT токена (секунды)"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Преобразование строки CORS источников в список
        
        Returns:
            List[str]: Список разрешённых источников
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def database_url(self) -> str:
        """
        Получение полного URL базы данных для SQLAlchemy
        
        Returns:
            str: URL подключения к базе данных
        """
        return f"sqlite:///{self.database_path}"
    
    @property
    def notification_days_list(self) -> List[int]:
        """
        Преобразование строки дней уведомлений в список целых чисел
        
        Returns:
            List[int]: Список дней [14, 7, 3]
        """
        return [int(day.strip()) for day in self.notification_days.split(",")]
    
    @property
    def telegram_admin_ids_list(self) -> List[int]:
        """
        Преобразование строки ID администраторов в список целых чисел
        
        Returns:
            List[int]: Список Telegram ID администраторов
        """
        if not self.telegram_admin_ids:
            return []
        return [
            int(admin_id.strip()) 
            for admin_id in self.telegram_admin_ids.split(",") 
            if admin_id.strip()
        ]
    
    class Config:
        """Конфигурация Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Игнорировать дополнительные поля

# ============================================
# Глобальный экземпляр настроек
# ============================================
try:
    settings = Settings()
except Exception as e:
    print(f"❌ ОШИБКА ЗАГРУЗКИ КОНФИГУРАЦИИ: {e}")
    print("\n📝 Убедитесь, что:")
    print("   1. Файл .env существует")
    print("   2. Все обязательные переменные заполнены")
    print("   3. JWT_SECRET_KEY имеет минимум 32 символа")
    print("   4. TELEGRAM_BOT_TOKEN получен от @BotFather")
    print("   5. TELEGRAM_ADMIN_IDS - Telegram ID администраторов (через запятую)")
    print("\n💡 Запустите: python generate_env.py")
    raise

# ============================================
# Проверка конфигурации при импорте (для отладки)
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("ПРОВЕРКА КОНФИГУРАЦИИ")
    print("=" * 60)
    
    print(f"\n📁 База данных:")
    print(f"   Path: {settings.database_path}")
    print(f"   URL: {settings.database_url}")
    print(f"   Exists: {os.path.exists(settings.database_path)}")
    
    print(f"\n🔐 JWT:")
    print(f"   Algorithm: {settings.jwt_algorithm}")
    print(f"   Expiration: {settings.jwt_expiration_hours} hours")
    print(f"   Secret Key: {settings.jwt_secret_key[:15]}... ({len(settings.jwt_secret_key)} chars)")
    
    print(f"\n🤖 Telegram Bot:")
    print(f"   Token: {settings.telegram_bot_token[:20]}...")
    print(f"   Admin IDs: {settings.telegram_admin_ids_list}")
    
    print(f"\n🔔 Notifications:")
    print(f"   Check Time: {settings.notification_check_time}")
    print(f"   Timezone: {settings.notification_timezone}")
    print(f"   Days: {settings.notification_days_list}")
    print(f"   Retry Attempts: {settings.notification_retry_attempts}")
    print(f"   Retry Delay: {settings.notification_retry_delay}s")
    
    print(f"\n🌐 API Server:")
    print(f"   Host: {settings.api_host}")
    print(f"   Port: {settings.api_port}")
    print(f"   Reload: {settings.api_reload}")
    
    print(f"\n🌐 Web API Integration:")
    print(f"   Base URL: {settings.web_api_base_url}")
    print(f"   Timeout: {settings.web_api_timeout}s")
    print(f"   Username: {settings.bot_api_username}")
    
    print(f"\n📊 CORS:")
    print(f"   Origins: {settings.cors_origins_list}")
    
    print("\n" + "=" * 60)
    print("✅ Конфигурация загружена успешно")
    print("=" * 60)