# Создайте временный тестовый файл test_config.py
from bot.config import get_bot_config

try:
    config = get_bot_config()
    print("✅ Конфигурация загружена успешно!")
    print(f"📱 Бот токен: {config.telegram_bot_token[:20]}...")
    print(f"👤 Admin ID: {config.telegram_admin_id}")
    print(f"📅 Дни уведомлений: {config.notification_days_list}")
    print(f"⏰ Время проверки: {config.notification_check_time}")
    print(f"🌍 Часовой пояс: {config.notification_timezone}")
except Exception as e:
    print(f"❌ Ошибка: {e}")