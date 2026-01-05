#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления Telegram ID администраторов из .env файла
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database import SessionLocal
from backend.models import User
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def update_admin_telegram_ids():
    """Обновить Telegram ID администраторов из переменной окружения"""
    
    # Получаем Telegram ID из .env
    admin_ids_str = os.getenv('TELEGRAM_ADMIN_IDS', '')
    
    if not admin_ids_str:
        print("❌ Переменная TELEGRAM_ADMIN_IDS не найдена в .env файле")
        return False
    
    # Парсим ID администраторов
    try:
        admin_telegram_ids = [tid.strip() for tid in admin_ids_str.split(',') if tid.strip()]
    except Exception as e:
        print(f"❌ Ошибка парсинга TELEGRAM_ADMIN_IDS: {e}")
        return False
    
    if not admin_telegram_ids:
        print("❌ Не удалось получить Telegram ID администраторов")
        return False
    
    print(f"📋 Найдено {len(admin_telegram_ids)} Telegram ID в конфигурации:")
    for tid in admin_telegram_ids:
        print(f"   - {tid}")
    
    # Подключаемся к БД
    db = SessionLocal()
    
    try:
        # Получаем всех администраторов
        admins = db.query(User).filter(User.role == 'admin').all()
        
        if not admins:
            print("⚠️  В системе нет пользователей с ролью 'admin'")
            return False
        
        print(f"\n👥 Найдено администраторов в БД: {len(admins)}")
        for admin in admins:
            print(f"   - ID: {admin.id}, Email: {admin.email}, ФИО: {admin.full_name}, Текущий Telegram ID: {admin.telegram_id}")
        
        # Проверяем соответствие количества
        if len(admins) != len(admin_telegram_ids):
            print(f"\n⚠️  Предупреждение: количество администраторов ({len(admins)}) не совпадает с количеством Telegram ID ({len(admin_telegram_ids)})")
            print("Будут обновлены только первые записи")
        
        # Обновляем Telegram ID
        updated_count = 0
        for i, admin in enumerate(admins):
            if i < len(admin_telegram_ids):
                old_telegram_id = admin.telegram_id
                new_telegram_id = admin_telegram_ids[i]
                admin.telegram_id = new_telegram_id
                
                if old_telegram_id != new_telegram_id:
                    print(f"\n✏️  Обновление администратора: {admin.full_name}")
                    print(f"   Старый Telegram ID: {old_telegram_id}")
                    print(f"   Новый Telegram ID: {new_telegram_id}")
                    updated_count += 1
                else:
                    print(f"\n✅ Администратор {admin.full_name} уже имеет правильный Telegram ID")
        
        # Сохраняем изменения
        if updated_count > 0:
            db.commit()
            print(f"\n✅ Успешно обновлено {updated_count} администратор(ов)")
        else:
            print("\nℹ️  Обновления не требуются - все ID актуальны")
        
        # Показываем финальное состояние
        print("\n📊 Текущее состояние администраторов:")
        db.refresh(admins[0])  # Обновляем данные из БД
        admins = db.query(User).filter(User.role == 'admin').all()
        for admin in admins:
            status = "✅" if admin.telegram_id else "❌"
            print(f"   {status} {admin.full_name} (Email: {admin.email})")
            print(f"      Telegram ID: {admin.telegram_id or 'НЕ УСТАНОВЛЕН'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при обновлении: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  Обновление Telegram ID администраторов")
    print("=" * 60)
    print()
    
    success = update_admin_telegram_ids()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Скрипт выполнен успешно")
    else:
        print("❌ Скрипт завершился с ошибками")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
