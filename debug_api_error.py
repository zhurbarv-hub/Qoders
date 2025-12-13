# -*- coding: utf-8 -*-
"""
Диагностика ошибки создания кассы
"""
import sys
sys.path.insert(0, 'd:\\QoProj\\KKT')

from web.app.dependencies import get_db
from web.app.models.cash_register import CashRegister
from web.app.models.user import User
from web.app.models.client import DeadlineType
from web.app.services.cash_register_deadline_service import CashRegisterDeadlineService
from datetime import date, timedelta

def main():
    print("=== Диагностика создания кассы с дедлайнами ===\n")
    
    db = next(get_db())
    
    # Проверка 1: Существуют ли типы дедлайнов?
    print("1. Проверка типов дедлайнов:")
    fn_type = db.query(DeadlineType).filter(
        DeadlineType.type_name == "Замена ФН"
    ).first()
    ofd_type = db.query(DeadlineType).filter(
        DeadlineType.type_name == "Продление договора"
    ).first()
    
    print(f"  'Замена ФН': {'✓ Найден (ID={})'.format(fn_type.id) if fn_type else '✗ НЕ найден'}")
    print(f"  'Продление договора': {'✓ Найден (ID={})'.format(ofd_type.id) if ofd_type else '✗ НЕ найден'}")
    
    # Проверка 2: Существует ли пользователь ID=5?
    print("\n2. Проверка пользователя ID=5:")
    user = db.query(User).filter(User.id == 5).first()
    if user:
        print(f"  ✓ Найден: {user.full_name}")
    else:
        print("  ✗ Пользователь не найден")
        return
    
    # Проверка 3: Создание сервиса
    print("\n3. Инициализация CashRegisterDeadlineService:")
    try:
        service = CashRegisterDeadlineService(db)
        print(f"  ✓ Сервис создан")
        print(f"  FN type ID: {service.fn_type_id}")
        print(f"  OFD type ID: {service.ofd_type_id}")
    except Exception as e:
        print(f"  ✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Проверка 4: Попытка создать кассу
    print("\n4. Попытка создать кассу с дедлайнами:")
    try:
        test_register = CashRegister(
            user_id=5,
            serial_number="DIAG-TEST-001",
            fiscal_drive_number="FN-DIAG-001",
            register_name="Диагностическая касса",
            installation_address="Тестовый адрес",
            notes="Диагностика",
            fn_replacement_date=date.today() + timedelta(days=45),
            ofd_renewal_date=date.today() + timedelta(days=60)
        )
        
        db.add(test_register)
        db.flush()
        
        print(f"  ✓ Касса создана, ID={test_register.id}")
        
        # Проверка 5: Вызов sync_deadlines_on_create
        print("\n5. Вызов sync_deadlines_on_create:")
        fn_deadline, ofd_deadline = service.sync_deadlines_on_create(
            cash_register_id=test_register.id,
            user_id=test_register.user_id,
            register_name=test_register.register_name,
            fn_replacement_date=test_register.fn_replacement_date,
            ofd_renewal_date=test_register.ofd_renewal_date
        )
        
        print(f"  ФН дедлайн: {'✓ Создан (ID={})'.format(fn_deadline.id) if fn_deadline else '✗ НЕ создан'}")
        print(f"  ОФД дедлайн: {'✓ Создан (ID={})'.format(ofd_deadline.id) if ofd_deadline else '✗ НЕ создан'}")
        
        db.commit()
        print("\n✅ Все проверки пройдены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()

if __name__ == "__main__":
    main()
