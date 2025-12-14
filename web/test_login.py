"""
Тестирование логина пользователя Eliseev
"""
import sys
from pathlib import Path

# Добавить путь к корню проекта
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from web.app.models.user import User
from web.app.services.auth_service import authenticate_user
from web.app.database import SessionLocal

# Создание сессии
db = SessionLocal()

try:
    # Проверка пользователя в базе
    user = db.query(User).filter(User.username == "Eliseev").first()
    
    if user:
        print(f"✅ Пользователь найден:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Has Password: {'Да' if user.password_hash else 'Нет'}")
        
        # Попытка аутентификации
        print("\n🔐 Тестирование аутентификации...")
        
        # Тест с известным паролем (который был установлен при создании)
        test_password = "Qwerty123"
        
        auth_user = authenticate_user(db, "Eliseev", test_password)
        
        if auth_user:
            print(f"✅ Аутентификация успешна с паролем '{test_password}'")
        else:
            print(f"❌ Аутентификация не удалась с паролем '{test_password}'")
            
            # Попробуем по email
            auth_user_email = authenticate_user(db, user.email, test_password)
            if auth_user_email:
                print(f"✅ Аутентификация успешна с email '{user.email}'")
            else:
                print(f"❌ Аутентификация не удалась с email '{user.email}'")
    else:
        print("❌ Пользователь 'Eliseev' не найден в базе данных")
        
        # Показать всех пользователей
        all_users = db.query(User).all()
        print(f"\n📋 Всего пользователей в базе: {len(all_users)}")
        for u in all_users:
            print(f"   - {u.username} ({u.email}) - {u.role}")
        
finally:
    db.close()
