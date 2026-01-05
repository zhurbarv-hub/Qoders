#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования отправки уведомлений администраторам
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

def find_test_client():
    """Найти клиента для тестирования"""
    db = SessionLocal()
    
    try:
        # Ищем клиента с Telegram ID
        client = db.query(User).filter(
            User.role == 'client',
            User.telegram_id.isnot(None)
        ).first()
        
        if client:
            print(f"✅ Найден клиент для теста:")
            print(f"   ID: {client.id}")
            print(f"   ФИО: {client.full_name}")
            print(f"   Компания: {client.company_name}")
            print(f"   Email: {client.email}")
            print(f"   Telegram ID: {client.telegram_id}")
            print(f"   Telegram Username: @{client.telegram_username}" if client.telegram_username else "   Telegram Username: Не указан")
            return client.id
        else:
            print("❌ Не найдено клиентов с Telegram ID")
            print("\nВсе клиенты в системе:")
            all_clients = db.query(User).filter(User.role == 'client').all()
            for c in all_clients:
                print(f"   - {c.full_name} (ID: {c.id}, Telegram ID: {c.telegram_id})")
            return None
    finally:
        db.close()

def check_admins():
    """Проверить администраторов с Telegram ID"""
    db = SessionLocal()
    
    try:
        admins = db.query(User).filter(
            User.role == 'admin',
            User.telegram_id.isnot(None),
            User.is_active == True
        ).all()
        
        print(f"\n👥 Администраторы с Telegram ID ({len(admins)}):")
        for admin in admins:
            print(f"   ✅ {admin.full_name}")
            print(f"      Email: {admin.email}")
            print(f"      Telegram ID: {admin.telegram_id}")
            print()
        
        return len(admins) > 0
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  Проверка системы уведомлений")
    print("=" * 60)
    print()
    
    # Проверяем администраторов
    has_admins = check_admins()
    
    if not has_admins:
        print("❌ Нет администраторов с Telegram ID!")
        print("   Запустите: python update_admin_telegram_ids.py")
        sys.exit(1)
    
    # Ищем клиента
    print()
    print("=" * 60)
    print("  Поиск клиента для тестирования")
    print("=" * 60)
    print()
    
    client_id = find_test_client()
    
    if client_id:
        print()
        print("=" * 60)
        print("  ✅ ГОТОВО К ТЕСТИРОВАНИЮ")
        print("=" * 60)
        print()
        print("Теперь клиент может создать обращение через бота:")
        print("1. Нажать кнопку '❓ Помощь'")
        print("2. Заполнить форму обращения")
        print("3. Администраторы получат уведомление в Telegram")
    else:
        print()
        print("=" * 60)
        print("  ⚠️  ТРЕБУЕТСЯ РЕГИСТРАЦИЯ КЛИЕНТА")
        print("=" * 60)
        print()
        print("Для тестирования нужен клиент с Telegram ID.")
        print("Попросите клиента зарегистрироваться в боте.")
