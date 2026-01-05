#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения chat_id Telegram-группы
Использование:
1. Добавьте бота в группу
2. Сделайте бота администратором группы
3. Отправьте любое сообщение в группу
4. Запустите этот скрипт
"""
import asyncio
from aiogram import Bot
from backend.config import settings


async def get_updates():
    """Получить обновления и показать chat_id группы"""
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        print("🔍 Получение обновлений от Telegram...")
        updates = await bot.get_updates()
        
        if not updates:
            print("\n❌ Нет обновлений. Убедитесь, что:")
            print("   1. Бот добавлен в группу")
            print("   2. Бот является администратором группы")
            print("   3. В группе было отправлено хотя бы одно сообщение после добавления бота")
            return
        
        print(f"\n✅ Найдено обновлений: {len(updates)}\n")
        
        # Показываем информацию о группах
        groups = {}
        for update in updates:
            if update.message and update.message.chat.type in ['group', 'supergroup']:
                chat = update.message.chat
                chat_id = chat.id
                
                if chat_id not in groups:
                    groups[chat_id] = {
                        'id': chat_id,
                        'title': chat.title,
                        'type': chat.type
                    }
        
        if groups:
            print("📋 Найденные группы:\n")
            for group_info in groups.values():
                print(f"  Группа: {group_info['title']}")
                print(f"  Chat ID: {group_info['id']}")
                print(f"  Тип: {group_info['type']}")
                print(f"  ----------------------------------------")
            
            print("\n💡 Скопируйте Chat ID нужной группы и добавьте в .env файл:")
            print("   ADMIN_GROUP_CHAT_ID=<chat_id>")
        else:
            print("❌ Группы не найдены в обновлениях")
            print("   Отправьте сообщение в группу и запустите скрипт снова")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  ПОЛУЧЕНИЕ CHAT_ID TELEGRAM-ГРУППЫ")
    print("=" * 60)
    asyncio.run(get_updates())
