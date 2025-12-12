#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Инициализация базы данных для веб-интерфейса
"""
import sys
import os

# Добавить корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app.database import engine, Base
from web.app.models.client import Client, DeadlineType, Deadline, Contact, NotificationLog
from web.app.models.user import WebUser
from sqlalchemy import text
import bcrypt


def init_database():
    """Создать все таблицы и добавить начальные данные"""
    
    print("🔧 Инициализация БД для веб-интерфейса...")
    print(f"📂 Путь к БД: {engine.url}")
    
    # Создать все таблицы
    print("\n📊 Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")
    
    # Проверить созданные таблицы
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
        tables = [row[0] for row in result]
        print(f"\n📋 Таблицы в БД ({len(tables)}):")
        for table in tables:
            print(f"   - {table}")
    
    # Добавить начальные данные
    from sqlalchemy.orm import Session
    
    with Session(engine) as session:
        # Проверить, есть ли уже данные
        existing_types = session.query(DeadlineType).count()
        existing_users = session.query(WebUser).count()
        
        if existing_types == 0:
            print("\n➕ Добавление типов дедлайнов...")
            deadline_types = [
                DeadlineType(type_name="ККТ регистрация", description="Регистрация кассового аппарата", is_system=True),
                DeadlineType(type_name="ОФД договор", description="Договор с оператором фискальных данных", is_system=True),
                DeadlineType(type_name="ФН замена", description="Замена фискального накопителя", is_system=True),
                DeadlineType(type_name="Техобслуживание", description="Техническое обслуживание ККТ", is_system=True)
            ]
            session.add_all(deadline_types)
            print(f"✅ Добавлено {len(deadline_types)} типов дедлайнов")
        else:
            print(f"\n⏭️  Типы дедлайнов уже существуют ({existing_types} шт.)")
        
        if existing_users == 0:
            print("\n➕ Добавление тестового администратора...")
            # Создать пароль
            password = "admin123"
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            admin = WebUser(
                username="admin",
                email="admin@kkt.local",
                password_hash=password_hash,
                full_name="Администратор",
                role="admin",
                is_active=True
            )
            session.add(admin)
            print(f"✅ Создан пользователь: admin / {password}")
        else:
            print(f"\n⏭️  Пользователи уже существуют ({existing_users} шт.)")
        
        # Сохранить изменения
        session.commit()
    
    print("\n✅ Инициализация завершена успешно!")
    print("\n" + "="*60)
    print("📌 УЧЕТНЫЕ ДАННЫЕ ДЛЯ ВХОДА:")
    print("   Логин: admin")
    print("   Пароль: admin123")
    print("="*60)


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
