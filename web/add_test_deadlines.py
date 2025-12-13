"""Скрипт для добавления тестовых дедлайнов"""
from datetime import datetime, timedelta, date
from app.database import SessionLocal
from app.models.client import Deadline, DeadlineType
from app.models.user import User

db = SessionLocal()

try:
    # Получаем клиентов
    users = db.query(User).filter(User.role == 'client').limit(5).all()
    print(f'Найдено клиентов: {len(users)}')
    
    # Получаем типы дедлайнов
    deadline_types = db.query(DeadlineType).all()
    print(f'Найдено типов дедлайнов: {len(deadline_types)}')
    
    if not users:
        print('❌ Нет клиентов в базе')
        exit(1)
    
    if not deadline_types:
        print('❌ Нет типов дедлайнов в базе')
        exit(1)
    
    # Создаём дедлайны на разные даты
    test_dates = [
        (date.today(), 'Сегодня'),
        (date.today() + timedelta(days=1), 'Завтра'),
        (date.today() + timedelta(days=3), 'Через 3 дня'),
        (date.today() + timedelta(days=7), 'Через неделю'),
        (date.today() + timedelta(days=14), 'Через 2 недели'),
    ]
    
    created = 0
    for i, (deadline_date, description) in enumerate(test_dates):
        if i >= len(users):
            break
            
        user = users[i]
        deadline_type = deadline_types[i % len(deadline_types)]
        
        # Проверяем, нет ли уже такого дедлайна
        existing = db.query(Deadline).filter(
            Deadline.user_id == user.id,
            Deadline.expiration_date == deadline_date,
            Deadline.deadline_type_id == deadline_type.id
        ).first()
        
        if existing:
            print(f'⏭️  Дедлайн для {user.company_name} на {deadline_date} уже существует')
            continue
        
        dl = Deadline(
            user_id=user.id,
            deadline_type_id=deadline_type.id,
            expiration_date=deadline_date,
            status='active',
            notes=f'Тестовый дедлайн: {description}'
        )
        db.add(dl)
        created += 1
        print(f'✅ Создан дедлайн для {user.company_name}: {deadline_type.type_name} - {deadline_date} ({description})')
    
    db.commit()
    print(f'\n✅ Создано {created} тестовых дедлайнов!')
    
except Exception as e:
    print(f'❌ Ошибка: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
