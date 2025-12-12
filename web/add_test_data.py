#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Добавление тестовых данных для демонстрации веб-интерфейса
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app.database import engine
from web.app.models.client import Client, Deadline, DeadlineType
from sqlalchemy.orm import Session


def add_test_data():
    """Добавить тестовые данные"""
    
    print("📊 Добавление тестовых данных...")
    
    with Session(engine) as session:
        # Проверить, есть ли уже клиенты
        existing_clients = session.query(Client).count()
        if existing_clients > 0:
            print(f"⏭️  Клиенты уже существуют ({existing_clients} шт.)")
            return
        
        # Получить типы дедлайнов
        types = session.query(DeadlineType).all()
        if not types:
            print("❌ Сначала нужно инициализировать типы дедлайнов!")
            return
        
        type_dict = {dt.type_name: dt for dt in types}
        
        # Создать тестовых клиентов
        clients_data = [
            {
                "name": "ООО \"Рога и Копыта\"",
                "inn": "7701234567",
                "contact_person": "Иванов Иван Иванович",
                "phone": "+7 (495) 123-45-67",
                "email": "ivanov@rogaikopyta.ru",
                "address": "г. Москва, ул. Ленина, д. 1"
            },
            {
                "name": "ИП Петров",
                "inn": "770987654321",
                "contact_person": "Петров Петр Петрович",
                "phone": "+7 (495) 987-65-43",
                "email": "petrov@mail.ru",
                "address": "г. Москва, ул. Пушкина, д. 10"
            },
            {
                "name": "ООО \"Торговый Дом\"",
                "inn": "7705555555",
                "contact_person": "Сидорова Мария Ивановна",
                "phone": "+7 (495) 555-55-55",
                "email": "info@td.ru",
                "address": "г. Москва, Проспект Мира, д. 25"
            }
        ]
        
        today = datetime.now().date()
        
        for i, client_data in enumerate(clients_data):
            client = Client(**client_data)
            session.add(client)
            session.flush()  # Получить ID клиента
            
            # Добавить дедлайны для каждого клиента
            deadlines_data = [
                {
                    "deadline_type_id": type_dict.get("Регистрация ККТ", types[0]).id,
                    "expiration_date": today + timedelta(days=5 + i*10),
                    "status": "active",
                    "notes": "Срочно нужно продлить регистрацию"
                },
                {
                    "deadline_type_id": type_dict.get("Продление договора", types[1]).id,
                    "expiration_date": today + timedelta(days=20 + i*15),
                    "status": "active",
                    "notes": "Договор с ОФД Платформа"
                },
                {
                    "deadline_type_id": type_dict.get("Замена ФН", types[2]).id,
                    "expiration_date": today + timedelta(days=40 + i*20),
                    "status": "active"
                }
            ]
            
            for deadline_data in deadlines_data:
                deadline = Deadline(
                    client_id=client.id,
                    **deadline_data
                )
                session.add(deadline)
            
            print(f"✅ Клиент: {client.name} ({len(deadlines_data)} дедлайнов)")
        
        # Добавить один истёкший дедлайн
        client = session.query(Client).first()
        if client:
            expired_deadline = Deadline(
                client_id=client.id,
                deadline_type_id=type_dict.get("Техническое обслуживание", types[3]).id,
                expiration_date=today - timedelta(days=5),
                status="expired",
                notes="Просрочено техобслуживание"
            )
            session.add(expired_deadline)
            print(f"⚠️  Добавлен просроченный дедлайн для {client.name}")
        
        session.commit()
        
        # Вывести статистику
        total_clients = session.query(Client).count()
        total_deadlines = session.query(Deadline).count()
        
        print(f"\n✅ Добавлено:")
        print(f"   - Клиентов: {total_clients}")
        print(f"   - Дедлайнов: {total_deadlines}")


if __name__ == "__main__":
    try:
        add_test_data()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
