#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования отправки уведомления в группу администраторов
Создаёт тестовое обращение клиента
"""
import asyncio
from datetime import datetime
from backend.database import SessionLocal
from backend.models import User, SupportRequest
from bot.handlers.client_buttons import notify_admins_about_support_request


async def test_group_notification():
    """Создать тестовое обращение и отправить уведомление в группу"""
    db = SessionLocal()
    
    try:
        # Находим первого клиента для теста
        client = db.query(User).filter(User.role == 'client').first()
        
        if not client:
            print("❌ Клиенты не найдены в БД. Создайте клиента сначала.")
            return
        
        print(f"📋 Создание тестового обращения от клиента: {client.company_name or client.full_name}")
        
        # Создаём тестовое обращение
        test_request = SupportRequest(
            client_id=client.id,
            subject="🧪 ТЕСТ: Проверка уведомлений в группу",
            message="Это тестовое обращение для проверки отправки уведомлений в Telegram-группу администраторов.\n\nЕсли вы видите это сообщение в группе - всё работает отлично! ✅",
            contact_phone=client.phone or "+7 999 123-45-67",
            status='new',
            created_at=datetime.now()
        )
        
        db.add(test_request)
        db.commit()
        db.refresh(test_request)
        
        print(f"✅ Создано обращение #{test_request.id}")
        print(f"   Тема: {test_request.subject}")
        print(f"   Статус: {test_request.status}")
        print()
        print("📨 Отправка уведомления в группу администраторов...")
        
        # Отправляем уведомление
        await notify_admins_about_support_request(
            support_request=test_request,
            client_id=client.id,
            db_session=db
        )
        
        print()
        print("=" * 60)
        print("✅ ТЕСТ ЗАВЕРШЁН")
        print("=" * 60)
        print()
        print("Проверьте Telegram-группу 'Обращения клиентов ККТ'")
        print("Должно прийти сообщение о новом обращении!")
        print()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  ТЕСТИРОВАНИЕ УВЕДОМЛЕНИЙ В ГРУППУ")
    print("=" * 60)
    print()
    asyncio.run(test_group_notification())
