# -*- coding: utf-8 -*-
"""
Прямое обновление пароля администратора в БД (без ORM)
Обходит проблему несоответствия модели и схемы БД
"""
import sqlite3
import bcrypt
from datetime import datetime


def get_password_hash(password: str) -> str:
    """Хеширование пароля через bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def main():
    """Основная функция"""
    db_path = 'database/kkt_services.db'
    
    try:
        print("=" * 60)
        print("🔧 ИСПРАВЛЕНИЕ ПАРОЛЯ БОТА (ПРЯМОЙ ДОСТУП К БД)")
        print("=" * 60)
        
        # Подключение к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Поиск пользователя admin
        cursor.execute('''
            SELECT id, email, role, is_active, password_hash, full_name 
            FROM users 
            WHERE email = ?
        ''', ('admin@kkt.ru',))
        
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ Пользователь 'admin@kkt.ru' не найден в базе данных!")
            print("\n💡 Создайте пользователя admin через веб-интерфейс")
            conn.close()
            return 1
        
        user_id, email, role, is_active, old_hash, full_name = admin_user
        
        print(f"\n✅ Найден пользователь:")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   Role: {role}")
        print(f"   Active: {is_active}")
        
        # Проверка текущего пароля
        new_password = "admin123"
        
        if old_hash:
            # Проверяем, может пароль уже admin123
            try:
                if verify_password(new_password, old_hash):
                    print(f"\n✅ Пароль уже установлен на '{new_password}'")
                    print("   Никаких изменений не требуется!")
                    
                    # Тестовая проверка
                    print("\n🧪 Тестирование авторизации...")
                    test_result = verify_password(new_password, old_hash)
                    print(f"   Результат: {'✅ УСПЕШНО' if test_result else '❌ ОШИБКА'}")
                    
                    conn.close()
                    return 0
                else:
                    print(f"\n⚠️  Текущий пароль отличается от '{new_password}'")
            except Exception as e:
                print(f"\n⚠️  Ошибка проверки старого пароля: {e}")
        else:
            print("\n⚠️  У пользователя отсутствует хеш пароля")
        
        # Генерация нового хеша
        print(f"\n🔐 Генерация нового хеша для пароля '{new_password}'...")
        new_hash = get_password_hash(new_password)
        print(f"   Хеш: {new_hash[:50]}...")
        
        # Обновление в базе данных
        print("\n💾 Обновление базы данных...")
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        ''', (new_hash, user_id))
        
        conn.commit()
        print("   ✅ Пароль успешно обновлён!")
        
        # Проверка после обновления
        print("\n🧪 Проверка нового пароля...")
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        updated_hash = cursor.fetchone()[0]
        
        if verify_password(new_password, updated_hash):
            print("   ✅ Пароль корректен и работает!")
        else:
            print("   ❌ ОШИБКА: Пароль не прошёл проверку!")
            conn.close()
            return 1
        
        print("\n" + "=" * 60)
        print("✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print("=" * 60)
        print("\n📋 Следующие шаги:")
        print("   1. Убедитесь, что в .env файле:")
        print("      BOT_API_USERNAME=admin@kkt.ru")
        print("      BOT_API_PASSWORD=admin123")
        print("   2. Перезапустите Web API")
        print("   3. Перезапустите Telegram бота")
        print("   4. Проверьте логи бота на наличие ошибок")
        print()
        
        conn.close()
        return 0
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
# -*- coding: utf-8 -*-
"""
Прямое обновление пароля администратора в БД (без ORM)
Обходит проблему несоответствия модели и схемы БД
"""
import sqlite3
import bcrypt
from datetime import datetime


def get_password_hash(password: str) -> str:
    """Хеширование пароля через bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def main():
    """Основная функция"""
    db_path = 'database/kkt_services.db'
    
    try:
        print("=" * 60)
        print("🔧 ИСПРАВЛЕНИЕ ПАРОЛЯ БОТА (ПРЯМОЙ ДОСТУП К БД)")
        print("=" * 60)
        
        # Подключение к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Поиск пользователя admin
        cursor.execute('''
            SELECT id, email, role, is_active, password_hash, full_name 
            FROM users 
            WHERE email = ?
        ''', ('admin@kkt.ru',))
        
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("❌ Пользователь 'admin@kkt.ru' не найден в базе данных!")
            print("\n💡 Создайте пользователя admin через веб-интерфейс")
            conn.close()
            return 1
        
        user_id, email, role, is_active, old_hash, full_name = admin_user
        
        print(f"\n✅ Найден пользователь:")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Full Name: {full_name}")
        print(f"   Role: {role}")
        print(f"   Active: {is_active}")
        
        # Проверка текущего пароля
        new_password = "admin123"
        
        if old_hash:
            # Проверяем, может пароль уже admin123
            try:
                if verify_password(new_password, old_hash):
                    print(f"\n✅ Пароль уже установлен на '{new_password}'")
                    print("   Никаких изменений не требуется!")
                    
                    # Тестовая проверка
                    print("\n🧪 Тестирование авторизации...")
                    test_result = verify_password(new_password, old_hash)
                    print(f"   Результат: {'✅ УСПЕШНО' if test_result else '❌ ОШИБКА'}")
                    
                    conn.close()
                    return 0
                else:
                    print(f"\n⚠️  Текущий пароль отличается от '{new_password}'")
            except Exception as e:
                print(f"\n⚠️  Ошибка проверки старого пароля: {e}")
        else:
            print("\n⚠️  У пользователя отсутствует хеш пароля")
        
        # Генерация нового хеша
        print(f"\n🔐 Генерация нового хеша для пароля '{new_password}'...")
        new_hash = get_password_hash(new_password)
        print(f"   Хеш: {new_hash[:50]}...")
        
        # Обновление в базе данных
        print("\n💾 Обновление базы данных...")
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        ''', (new_hash, user_id))
        
        conn.commit()
        print("   ✅ Пароль успешно обновлён!")
        
        # Проверка после обновления
        print("\n🧪 Проверка нового пароля...")
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        updated_hash = cursor.fetchone()[0]
        
        if verify_password(new_password, updated_hash):
            print("   ✅ Пароль корректен и работает!")
        else:
            print("   ❌ ОШИБКА: Пароль не прошёл проверку!")
            conn.close()
            return 1
        
        print("\n" + "=" * 60)
        print("✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
        print("=" * 60)
        print("\n📋 Следующие шаги:")
        print("   1. Убедитесь, что в .env файле:")
        print("      BOT_API_USERNAME=admin@kkt.ru")
        print("      BOT_API_PASSWORD=admin123")
        print("   2. Перезапустите Web API")
        print("   3. Перезапустите Telegram бота")
        print("   4. Проверьте логи бота на наличие ошибок")
        print()
        
        conn.close()
        return 0
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
