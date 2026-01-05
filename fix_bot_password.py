# -*- coding: utf-8 -*-
"""
Скрипт для исправления пароля бота
Обновляет пароль пользователя admin на admin123 для корректной работы с Web API
"""
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.app.database import SessionLocal
from web.app.models.user import User
from web.app.services.auth_service import get_password_hash, verify_password
from datetime import datetime


def main():
    """Основная функция"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("🔧 ИСПРАВЛЕНИЕ ПАРОЛЯ БОТА")
        print("=" * 60)
        
        # Поиск пользователя admin (по email, т.к. в старой БД нет поля username)
        admin_user = db.query(User).filter(User.email == 'admin@kkt.ru').first()
        
        if not admin_user:
            print("❌ Пользователь 'admin@kkt.ru' не найден в базе данных!")
            print("\n💡 Создайте пользователя admin через веб-интерфейс")
            return 1
        
        print(f"\n✅ Найден пользователь: {admin_user.email}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        print(f"   Active: {admin_user.is_active}")
        
        # Проверка текущего пароля
        new_password = "admin123"
        
        if admin_user.password_hash:
            # Проверяем, может пароль уже admin123
            if verify_password(new_password, admin_user.password_hash):
                print(f"\n✅ Пароль уже установлен на '{new_password}'")
                print("   Никаких изменений не требуется!")
                
                # Тестовая проверка
                print("\n🧪 Тестирование авторизации...")
                test_result = verify_password(new_password, admin_user.password_hash)
                print(f"   Результат: {'✅ УСПЕШНО' if test_result else '❌ ОШИБКА'}")
                return 0
            else:
                print(f"\n⚠️  Текущий пароль отличается от '{new_password}'")
        else:
            print("\n⚠️  У пользователя отсутствует хеш пароля")
        
        # Генерация нового хеша
        print(f"\n🔐 Генерация нового хеша для пароля '{new_password}'...")
        new_hash = get_password_hash(new_password)
        print(f"   Хеш: {new_hash[:50]}...")
        
        # Обновление в базе данных
        print("\n💾 Обновление базы данных...")
        admin_user.password_hash = new_hash
        admin_user.updated_at = datetime.utcnow()
        db.commit()
        
        print("   ✅ Пароль успешно обновлён!")
        
        # Проверка после обновления
        print("\n🧪 Проверка нового пароля...")
        db.refresh(admin_user)
        
        if verify_password(new_password, admin_user.password_hash):
            print("   ✅ Пароль корректен и работает!")
        else:
            print("   ❌ ОШИБКА: Пароль не прошёл проверку!")
            return 1
        
        print("\n" + "=" * 60)
        print("✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print("=" * 60)
        print("\n📋 Следующие шаги:")
        print("   1. Убедитесь, что в .env файле:")
        print("      BOT_API_USERNAME=admin")
        print("      BOT_API_PASSWORD=admin123")
        print("   2. Перезапустите Web API")
        print("   3. Перезапустите Telegram бота")
        print("   4. Проверьте логи бота на наличие ошибок")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
