#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Добавление тестовых клиентов (users с role='client')
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app.database import engine
from web.app.models.user import User  # Используем User вместо WebUser
from web.app.services.auth_service import get_password_hash
from sqlalchemy.orm import Session


def add_test_clients():
    """Добавить тестовых клиентов"""
    
    print("📊 Добавление тестовых клиентов...")
    
    with Session(engine) as session:
        # Проверить, есть ли уже клиенты
        existing_clients = session.query(User).filter(User.role == 'client').count()
        if existing_clients > 0:
            print(f"⏭️  Клиенты уже существуют ({existing_clients} шт.)")
            response = input("Добавить ещё клиентов? (y/n): ")
            if response.lower() != 'y':
                return
        
        # Создать тестовых клиентов
        clients_data = [
            {
                "username": "client1",
                "email": "client1@test.ru",
                "password": "password123",
                "full_name": "Иванов Иван Иванович",
                "role": "client",
                "is_active": True,
                # Дополнительные поля для клиентов
                "company_name": "ООО Рога и Копыта",
                "inn": "7701234567",
                "phone": "+7 (495) 123-45-67",
                "address": "г. Москва, ул. Ленина, д. 1"
            },
            {
                "username": "client2",
                "email": "client2@test.ru",
                "password": "password123",
                "full_name": "Петров Петр Петрович",
                "role": "client",
                "is_active": True,
                "company_name": "ИП Петров",
                "inn": "770987654321",
                "phone": "+7 (495) 987-65-43",
                "address": "г. Москва, ул. Пушкина, д. 10"
            },
            {
                "username": "client3",
                "email": "client3@test.ru",
                "password": "password123",
                "full_name": "Сидорова Мария Ивановна",
                "role": "client",
                "is_active": True,
                "company_name": "ООО Торговый Дом",
                "inn": "7705555555",
                "phone": "+7 (495) 555-55-55",
                "address": "г. Москва, Проспект Мира, д. 25"
            }
        ]
        
        for client_data in clients_data:
            # Проверяем, существует ли уже такой email
            existing = session.query(User).filter(User.email == client_data["email"]).first()
            if existing:
                print(f"⏭️  Клиент {client_data['email']} уже существует")
                continue
            
            # Хешируем пароль
            password = client_data.pop("password")
            password_hash = get_password_hash(password)
            
            # Создаём клиента
            client = User(
                password_hash=password_hash,
                **client_data
            )
            session.add(client)
            print(f"✅ Клиент: {client.company_name} ({client.email})")
        
        session.commit()
        
        # Вывести статистику
        total_clients = session.query(User).filter(User.role == 'client').count()
        
        print(f"\n✅ Всего клиентов в базе: {total_clients}")


if __name__ == "__main__":
    try:
        add_test_clients()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
