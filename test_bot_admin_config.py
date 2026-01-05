#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Тест конфигурации админов в боте"""

import sys
sys.path.insert(0, '/home/kktapp/kkt-system')

from backend.config import settings
from bot.config import get_bot_config

print("=" * 70)
print("ПРОВЕРКА КОНФИГУРАЦИИ TELEGRAM АДМИНОВ")
print("=" * 70)

# Из .env
print("\n📄 Из .env файла:")
print(f"   ADMIN_TELEGRAM_IDS (raw): {settings.telegram_admin_ids}")

# Парсинг
print("\n🔧 После парсинга:")
print(f"   Admin IDs (list): {settings.telegram_admin_ids_list}")
print(f"   Тип: {type(settings.telegram_admin_ids_list)}")
print(f"   Количество: {len(settings.telegram_admin_ids_list)}")

# Детали
print("\n👥 Детали администраторов:")
for i, admin_id in enumerate(settings.telegram_admin_ids_list, 1):
    print(f"   {i}. ID: {admin_id} (тип: {type(admin_id).__name__})")

# Конфигурация бота
print("\n🤖 Конфигурация бота:")
bot_config = get_bot_config()
print(f"   telegram_admin_ids: {bot_config['telegram_admin_ids']}")

# Проверка из БД
print("\n💾 Администраторы из базы данных:")
from web.app.database import SessionLocal
from web.app.models.user import User

db = SessionLocal()
admins = db.query(User).filter(User.role == 'admin', User.is_active == True).all()

for admin in admins:
    tg_id = admin.telegram_id
    in_config = int(tg_id) in settings.telegram_admin_ids_list if tg_id else False
    status = "✅" if in_config else "❌"
    print(f"   {status} {admin.full_name} ({admin.username})")
    print(f"      Telegram ID: {tg_id or 'НЕ УКАЗАН'}")
    if tg_id:
        print(f"      В конфигурации: {'Да' if in_config else 'НЕТ'}")

db.close()

print("\n" + "=" * 70)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 70)
