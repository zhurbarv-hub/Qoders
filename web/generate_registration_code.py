"""Скрипт для генерации кода регистрации для клиента"""
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.user import User
import random
import string

db = SessionLocal()

try:
    # Получаем первого клиента
    client = db.query(User).filter(
        User.role == 'client',
        User.telegram_id == None  # Не авторизован в боте
    ).first()
    
    if not client:
        print('❌ Нет неавторизованных клиентов в базе')
        exit(1)
    
    # Генерируем 6-значный код
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Устанавливаем код и срок действия (72 часа)
    client.registration_code = code
    client.code_expires_at = datetime.now() + timedelta(hours=72)
    
    db.commit()
    
    print(f'✅ Код регистрации создан для клиента:')
    print(f'   Компания: {client.company_name}')
    print(f'   Email: {client.email}')
    print(f'   ID: {client.id}')
    print(f'')
    print(f'   🔑 КОД РЕГИСТРАЦИИ: {code}')
    print(f'')
    print(f'   Срок действия: до {client.code_expires_at.strftime("%d.%m.%Y %H:%M")}')
    print(f'')
    print(f'📱 Для тестирования:')
    print(f'   1. Зайдите в бота с другого аккаунта (не админ)')
    print(f'   2. Отправьте /start')
    print(f'   3. Введите код: {code}')
    
except Exception as e:
    print(f'❌ Ошибка: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
