"""
Скрипт для обновления старых 8-символьных кодов на 6-символьные
"""
from backend.database import SessionLocal
from backend.models import User
from datetime import datetime, timedelta
import string
import secrets

def generate_registration_code(length: int = 6) -> str:
    """Генерация уникального кода регистрации для Telegram"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

db = SessionLocal()

try:
    # Найти всех пользователей с кодом регистрации
    users_with_code = db.query(User).filter(
        User.registration_code != None,
        User.telegram_id == None,  # Ещё не зарегистрированы
        User.role == 'client'
    ).all()
    
    print(f"\n=== Обновление кодов регистрации ===")
    print(f"Найдено пользователей с активными кодами: {len(users_with_code)}\n")
    
    updated_count = 0
    
    for user in users_with_code:
        old_code = user.registration_code
        old_length = len(old_code) if old_code else 0
        
        # Проверяем длину кода
        if old_length != 6:
            # Генерируем новый 6-символьный код
            new_code = None
            for _ in range(10):
                code = generate_registration_code(6)
                existing = db.query(User).filter(User.registration_code == code).first()
                if not existing:
                    new_code = code
                    break
            
            if new_code:
                user.registration_code = new_code
                # Продлеваем срок действия на 72 часа от текущего момента
                user.code_expires_at = datetime.now() + timedelta(hours=72)
                
                print(f"ID {user.id}: {user.company_name}")
                print(f"  Старый код ({old_length} симв.): {old_code}")
                print(f"  Новый код (6 симв.): {new_code}")
                print(f"  Новый срок истечения: {user.code_expires_at}")
                print(f"  Email: {user.email}")
                print("-" * 60)
                
                updated_count += 1
            else:
                print(f"ОШИБКА: Не удалось сгенерировать уникальный код для пользователя {user.id}")
        else:
            print(f"ID {user.id}: {user.company_name} - код уже 6 символов ({old_code}), пропускаем")
    
    # Сохраняем изменения
    if updated_count > 0:
        db.commit()
        print(f"\n✅ Успешно обновлено кодов: {updated_count}")
    else:
        print(f"\n✅ Все коды уже имеют правильную длину (6 символов)")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
