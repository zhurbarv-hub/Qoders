# -*- coding: utf-8 -*-
"""
Тестирование автоматического создания дедлайнов при сохранении карточки ККТ
"""
import sys
from pathlib import Path
from datetime import date, timedelta

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from web.app.models.cash_register import CashRegister
from web.app.models.client import Deadline, DeadlineType
from web.app.models.user import User

# Путь к базе данных
DATABASE_PATH = BASE_DIR / "database" / "kkt_services.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Создание подключения
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def main():
    """Проверка автоматического создания дедлайнов"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("ПРОВЕРКА АВТОМАТИЧЕСКОГО СОЗДАНИЯ ДЕДЛАЙНОВ ДЛЯ ККТ")
        print("="*70 + "\n")
        
        # 1. Проверяем наличие типов дедлайнов
        print("1️⃣ Проверка типов дедлайнов...")
        fn_type = db.query(DeadlineType).filter(
            DeadlineType.type_name == "Замена ФН",
            DeadlineType.is_active == True
        ).first()
        
        ofd_type = db.query(DeadlineType).filter(
            DeadlineType.type_name == "Продление договора",
            DeadlineType.is_active == True
        ).first()
        
        if not fn_type:
            print("❌ Тип 'Замена ФН' не найден или неактивен!")
            print("   Решение: создайте тип через интерфейс")
        else:
            print(f"✅ Тип 'Замена ФН' найден: ID={fn_type.id}")
        
        if not ofd_type:
            print("❌ Тип 'Продление договора' не найден или неактивен!")
            print("   Решение: создайте тип через интерфейс")
        else:
            print(f"✅ Тип 'Продление договора' найден: ID={ofd_type.id}")
        
        if not fn_type and not ofd_type:
            print("\n⚠️ Без типов дедлайнов автоматическое создание невозможно!")
            return
        
        # 2. Ищем последние добавленные кассы с датами
        print("\n2️⃣ Поиск касс с заполненными датами...")
        registers = db.query(CashRegister).filter(
            (CashRegister.fn_replacement_date != None) | 
            (CashRegister.ofd_renewal_date != None)
        ).order_by(CashRegister.updated_at.desc()).limit(5).all()
        
        if not registers:
            print("⚠️ Нет касс с заполненными датами замены ФН или продления ОФД")
            return
        
        print(f"✅ Найдено касс с датами: {len(registers)}\n")
        
        # 3. Проверяем каждую кассу
        for reg in registers:
            print("-" * 70)
            print(f"Касса ID={reg.id}: {reg.register_name}")
            print(f"  Дата замены ФН: {reg.fn_replacement_date or '-'}")
            print(f"  Дата продления ОФД: {reg.ofd_renewal_date or '-'}")
            
            # Ищем связанные дедлайны
            deadlines = db.query(Deadline).filter(
                Deadline.cash_register_id == reg.id,
                Deadline.status == 'active'
            ).all()
            
            print(f"  Найдено активных дедлайнов: {len(deadlines)}")
            
            if deadlines:
                for dl in deadlines:
                    dt = db.query(DeadlineType).filter(
                        DeadlineType.id == dl.deadline_type_id
                    ).first()
                    print(f"    - {dt.type_name if dt else 'Неизвестный тип'}: {dl.expiration_date}")
            
            # Проверяем соответствие
            expected_count = 0
            if reg.fn_replacement_date and fn_type:
                expected_count += 1
                fn_deadline = next((d for d in deadlines if d.deadline_type_id == fn_type.id), None)
                if fn_deadline:
                    if fn_deadline.expiration_date == reg.fn_replacement_date:
                        print(f"  ✅ Дедлайн 'Замена ФН' совпадает")
                    else:
                        print(f"  ⚠️ Дедлайн 'Замена ФН' не совпадает: {fn_deadline.expiration_date} != {reg.fn_replacement_date}")
                else:
                    print(f"  ❌ Дедлайн 'Замена ФН' отсутствует (ожидался)")
            
            if reg.ofd_renewal_date and ofd_type:
                expected_count += 1
                ofd_deadline = next((d for d in deadlines if d.deadline_type_id == ofd_type.id), None)
                if ofd_deadline:
                    if ofd_deadline.expiration_date == reg.ofd_renewal_date:
                        print(f"  ✅ Дедлайн 'Продление договора' совпадает")
                    else:
                        print(f"  ⚠️ Дедлайн 'Продление договора' не совпадает: {ofd_deadline.expiration_date} != {reg.ofd_renewal_date}")
                else:
                    print(f"  ❌ Дедлайн 'Продление договора' отсутствует (ожидался)")
            
            if len(deadlines) < expected_count:
                print(f"\n  ⚠️ ПРОБЛЕМА: Ожидалось {expected_count} дедлайнов, найдено {len(deadlines)}")
                print(f"     Касса обновлена: {reg.updated_at}")
        
        # 4. Общая статистика
        print("\n" + "="*70)
        print("ОБЩАЯ СТАТИСТИКА")
        print("="*70)
        
        total_registers = db.query(CashRegister).filter(
            CashRegister.is_active == True
        ).count()
        
        registers_with_dates = db.query(CashRegister).filter(
            CashRegister.is_active == True,
            (CashRegister.fn_replacement_date != None) | 
            (CashRegister.ofd_renewal_date != None)
        ).count()
        
        total_deadlines = db.query(Deadline).filter(
            Deadline.cash_register_id != None,
            Deadline.status == 'active'
        ).count()
        
        print(f"Всего активных касс: {total_registers}")
        print(f"Касс с заполненными датами: {registers_with_dates}")
        print(f"Всего кассовых дедлайнов: {total_deadlines}")
        
        if registers_with_dates > 0 and total_deadlines == 0:
            print("\n❌ КРИТИЧЕСКАЯ ПРОБЛЕМА: Есть кассы с датами, но нет дедлайнов!")
            print("   Возможные причины:")
            print("   1. Типы дедлайнов неактивны или отсутствуют")
            print("   2. Даты были добавлены напрямую в БД (не через API)")
            print("   3. Произошла ошибка при сохранении через API")
            print("\n   Решение:")
            print("   - Проверьте логи веб-сервера")
            print("   - Попробуйте обновить кассу через интерфейс")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
