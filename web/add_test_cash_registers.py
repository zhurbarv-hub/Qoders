#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Добавление тестовых данных для кассовых аппаратов
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app.database import engine
from web.app.models.client import Deadline, DeadlineType
from web.app.models.cash_register import CashRegister
from web.app.models.user import User
from sqlalchemy.orm import Session


def add_cash_registers_test_data():
    """Добавить тестовые кассовые аппараты и дедлайны"""
    
    print("📊 Добавление тестовых кассовых аппаратов...")
    
    with Session(engine) as session:
        # Проверить, есть ли уже кассы
        existing_registers = session.query(CashRegister).count()
        if existing_registers > 0:
            print(f"⏭️  Кассовые аппараты уже существуют ({existing_registers} шт.)")
            return
        
        # Получить всех пользователей (клиентов)
        users = session.query(User).filter(User.role == 'client').all()
        if not users:
            print("❌ Сначала нужно создать пользователей (клиентов)!")
            print("   Запустите: python web/add_test_clients.py")
            return
        
        # Получить типы дедлайнов
        types = session.query(DeadlineType).all()
        if not types:
            print("❌ Сначала нужно инициализировать типы дедлайнов!")
            return
        
        type_dict = {dt.type_name: dt for dt in types}
        
        today = datetime.now().date()
        
        # Для каждого пользователя создать 2-5 касс
        total_registers = 0
        total_deadlines = 0
        
        for user_idx, user in enumerate(users[:3]):  # Берем первых 3 клиентов
            num_registers = 2 + user_idx  # 2, 3, 4 кассы для разных клиентов
            
            for reg_idx in range(num_registers):
                # Создаем кассовый аппарат
                cash_register = CashRegister(
                    user_id=user.id,
                    serial_number=f"00000{user.id}{reg_idx:02d}12345",
                    fiscal_drive_number=f"9999{user.id}{reg_idx:02d}54321",
                    installation_address=f"г. Москва, ул. Торговая, д. {user_idx + 1}, касса {reg_idx + 1}",
                    register_name=f"Касса {reg_idx + 1}",
                    is_active=True
                )
                session.add(cash_register)
                session.flush()  # Получить ID кассы
                
                total_registers += 1
                
                # Добавляем 2-3 дедлайна для каждой кассы
                deadlines_data = [
                    {
                        "type_name": "Замена ФН (Замена фискального накопителя)",
                        "days_offset": 30 + reg_idx * 10,
                        "notes": "Замена фискального накопителя"
                    },
                    {
                        "type_name": "Продление договора",
                        "days_offset": 60 + reg_idx * 15,
                        "notes": "Продление договора с ОФД"
                    }
                ]
                
                # Для первой кассы первого клиента добавим просроченный дедлайн
                if user_idx == 0 and reg_idx == 0:
                    deadlines_data.append({
                        "type_name": "Регистрация ККТ",
                        "days_offset": -5,  # Просроченный
                        "notes": "⚠️ ПРОСРОЧЕНА регистрация!"
                    })
                else:
                    deadlines_data.append({
                        "type_name": "Регистрация ККТ",
                        "days_offset": 90 + reg_idx * 20,
                        "notes": "Регистрация в налоговой"
                    })
                
                for deadline_info in deadlines_data:
                    deadline_type = type_dict.get(deadline_info["type_name"])
                    if not deadline_type:
                        continue
                    
                    deadline = Deadline(
                        user_id=user.id,
                        cash_register_id=cash_register.id,
                        deadline_type_id=deadline_type.id,
                        expiration_date=today + timedelta(days=deadline_info["days_offset"]),
                        status='expired' if deadline_info["days_offset"] < 0 else 'active',
                        notes=deadline_info["notes"]
                    )
                    session.add(deadline)
                    total_deadlines += 1
            
            print(f"✅ Пользователь: {user.company_name or user.full_name} ({num_registers} касс, {num_registers * 3} дедлайнов)")
        
        # Добавляем несколько общих дедлайнов (не привязанных к кассам)
        if users:
            first_user = users[0]
            general_deadlines = [
                {
                    "type_name": "Техническое обслуживание",
                    "days_offset": 45,
                    "notes": "Общее техобслуживание офиса"
                }
            ]
            
            for deadline_info in general_deadlines:
                deadline_type = type_dict.get(deadline_info["type_name"])
                if deadline_type:
                    deadline = Deadline(
                        user_id=first_user.id,
                        cash_register_id=None,  # Общий дедлайн
                        deadline_type_id=deadline_type.id,
                        expiration_date=today + timedelta(days=deadline_info["days_offset"]),
                        status='active',
                        notes=deadline_info["notes"]
                    )
                    session.add(deadline)
                    total_deadlines += 1
            
            print(f"✅ Добавлены общие дедлайны для {first_user.company_name or first_user.full_name}")
        
        session.commit()
        
        print(f"\n✅ Успешно добавлено:")
        print(f"   - Кассовых аппаратов: {total_registers}")
        print(f"   - Дедлайнов: {total_deadlines}")


if __name__ == "__main__":
    try:
        add_cash_registers_test_data()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
