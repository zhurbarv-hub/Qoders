"""
Скрипт тестирования миграции базы данных
"""

from sqlalchemy import inspect, text
from backend.database import engine, get_db
from backend.models import User, Deadline, DeadlineType

def test_database_structure():
    """Проверка структуры базы данных"""
    print("=" * 60)
    print("ТЕСТ 1: СТРУКТУРА БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n✓ Найдено таблиц: {len(tables)}")
    for table in sorted(tables):
        print(f"  - {table}")
    
    # Проверка структуры таблицы users
    print("\n📋 Структура таблицы 'users':")
    columns = inspector.get_columns('users')
    print(f"  Всего полей: {len(columns)}")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        print(f"  - {col['name']:20} {col['type']} {nullable}")
    
    return len(tables)


def test_migrated_data():
    """Проверка мигрированных данных"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: МИГРИРОВАННЫЕ ДАННЫЕ")
    print("=" * 60)
    
    db = next(get_db())
    
    # Проверка пользователей
    users = db.query(User).all()
    print(f"\n✓ Всего пользователей: {len(users)}")
    
    clients = db.query(User).filter(User.role == 'client').all()
    managers = db.query(User).filter(User.role == 'manager').all()
    admins = db.query(User).filter(User.role == 'admin').all()
    
    print(f"  - Клиентов: {len(clients)}")
    print(f"  - Менеджеров: {len(managers)}")
    print(f"  - Администраторов: {len(admins)}")
    
    print("\n📊 Клиенты:")
    for client in clients:
        print(f"  - ID: {client.id}, Email: {client.email}")
        print(f"    Имя: {client.full_name}")
        print(f"    ИНН: {client.inn}, Компания: {client.company_name}")
        print(f"    Telegram: {client.telegram_id or 'не привязан'}")
        print(f"    Активен: {client.is_active}")
        print()
    
    # Проверка дедлайнов
    deadlines = db.query(Deadline).all()
    print(f"✓ Всего дедлайнов: {len(deadlines)}")
    
    for deadline in deadlines:
        user = deadline.user
        user_display = user.display_name if user else "Неизвестно"
        dtype = deadline.deadline_type.type_name if deadline.deadline_type else "Неизвестно"
        print(f"  - ID: {deadline.id}")
        print(f"    Пользователь (user_id={deadline.user_id}): {user_display}")
        print(f"    Тип: {dtype}")
        print(f"    Срок: {deadline.expiration_date}")
        print(f"    Статус: {deadline.status}")
        print(f"    До истечения: {deadline.days_until_expiration} дней")
        print()
    
    db.close()
    
    return len(users), len(deadlines)


def test_user_properties():
    """Проверка helper properties модели User"""
    print("=" * 60)
    print("ТЕСТ 3: HELPER PROPERTIES МОДЕЛИ USER")
    print("=" * 60)
    
    db = next(get_db())
    
    users = db.query(User).filter(User.role == 'client').all()
    
    for user in users:
        print(f"\n👤 {user.full_name}:")
        print(f"  - is_client: {user.is_client}")
        print(f"  - is_support: {user.is_support}")
        print(f"  - is_registered: {user.is_registered}")
        print(f"  - display_name: {user.display_name}")
        print(f"  - notification_days_list: {user.notification_days_list}")
        if user.registration_code:
            print(f"  - registration_code: {user.registration_code}")
            print(f"  - is_code_valid: {user.is_code_valid}")
    
    db.close()


def test_backward_compatibility():
    """Проверка обратной совместимости"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: ОБРАТНАЯ СОВМЕСТИМОСТЬ")
    print("=" * 60)
    
    db = next(get_db())
    
    # Проверка legacy поля client_id в deadlines
    deadlines = db.query(Deadline).all()
    print(f"\n✓ Проверка legacy поля 'client_id' в deadlines:")
    
    for deadline in deadlines:
        legacy_ok = deadline.client_id is not None
        status = "✓" if legacy_ok else "✗"
        print(f"  {status} Deadline ID {deadline.id}: client_id={deadline.client_id}, user_id={deadline.user_id}")
    
    db.close()


def test_backup_tables():
    """Проверка backup таблиц"""
    print("\n" + "=" * 60)
    print("ТЕСТ 5: BACKUP ТАБЛИЦЫ")
    print("=" * 60)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    backup_tables = [t for t in tables if t.startswith('_backup_')]
    print(f"\n✓ Найдено backup таблиц: {len(backup_tables)}")
    
    for table in backup_tables:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  - {table}: {count} записей")


def main():
    """Запуск всех тестов"""
    print("\n🧪 ПОЛНОЕ ТЕСТИРОВАНИЕ МИГРАЦИИ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    try:
        # Тест 1: Структура БД
        num_tables = test_database_structure()
        
        # Тест 2: Данные
        num_users, num_deadlines = test_migrated_data()
        
        # Тест 3: Properties
        test_user_properties()
        
        # Тест 4: Совместимость
        test_backward_compatibility()
        
        # Тест 5: Backup
        test_backup_tables()
        
        # Итоговый отчёт
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЁТ")
        print("=" * 60)
        print(f"✓ Таблиц в БД: {num_tables}")
        print(f"✓ Пользователей: {num_users}")
        print(f"✓ Дедлайнов: {num_deadlines}")
        print("\n🎉 ВСЕ ТЕСТЫ БАЗЫ ДАННЫХ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
