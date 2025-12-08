# -*- coding: utf-8 -*-
"""
Проверка завершения Фазы 1
Тестирование настройки окружения и базы данных
"""

import os
import sys

def test_phase1():
    """Комплексная проверка Фазы 1"""
    
    print("=" * 70)
    print(" " * 20 + "ПРОВЕРКА ФАЗЫ 1")
    print(" " * 10 + "Foundation Setup - Настройка окружения")
    print("=" * 70)
    
    results = {}
    total_checks = 0
    passed_checks = 0
    
    # ============================================
    # 1. Python Version
    # ============================================
    print("\n🐍 Проверка Python...")
    total_checks += 1
    
    python_version = sys.version_info
    if python_version >= (3, 9):
        print(f"   ✓ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        results['python'] = True
        passed_checks += 1
    else:
        print(f"   ✗ Python {python_version.major}.{python_version.minor} (требуется 3.9+)")
        results['python'] = False
    
    # ============================================
    # 2. Directory Structure
    # ============================================
    print("\n📁 Проверка структуры папок...")
    total_checks += 1
    
    required_dirs = [
        "backend",
        "backend/api",
        "backend/utils",
        "bot",
        "scheduler",
        "frontend",
        "frontend/static",
        "frontend/static/css",
        "frontend/static/js",
        "frontend/templates",
        "database",
        "logs",
        "backups"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if not missing_dirs:
        print(f"   ✓ Все {len(required_dirs)} папок созданы")
        results['directories'] = True
        passed_checks += 1
    else:
        print(f"   ✗ Отсутствуют папки ({len(missing_dirs)}):")
        for d in missing_dirs:
            print(f"      - {d}")
        results['directories'] = False
    
    # ============================================
    # 3. Configuration Files
    # ============================================
    print("\n⚙️  Проверка файлов конфигурации...")
    total_checks += 1
    
    config_files = {
        '.env.example': 'Шаблон переменных окружения',
        '.gitignore': 'Git ignore rules',
        'backend/config.py': 'Модуль конфигурации',
        'backend/database.py': 'Модуль подключения к БД'
    }
    
    missing_configs = []
    for file_path, description in config_files.items():
        if not os.path.exists(file_path):
            missing_configs.append(f"{file_path} ({description})")
    
    if not missing_configs:
        print(f"   ✓ Все {len(config_files)} файлов конфигурации созданы")
        results['config_files'] = True
        passed_checks += 1
    else:
        print(f"   ✗ Отсутствуют файлы ({len(missing_configs)}):")
        for f in missing_configs:
            print(f"      - {f}")
        results['config_files'] = False
    
    # ============================================
    # 4. Database Files
    # ============================================
    print("\n🗄️  Проверка файлов базы данных...")
    total_checks += 1
    
    db_files = {
        'database/schema_kkt.sql': 'SQL схема',
        'database/seed_data.sql': 'Начальные данные',
        'database/init_database.py': 'Скрипт инициализации'
    }
    
    missing_db_files = []
    for file_path, description in db_files.items():
        if not os.path.exists(file_path):
            missing_db_files.append(f"{file_path} ({description})")
    
    if not missing_db_files:
        print(f"   ✓ Все {len(db_files)} файлов БД созданы")
        results['db_files'] = True
        passed_checks += 1
    else:
        print(f"   ✗ Отсутствуют файлы ({len(missing_db_files)}):")
        for f in missing_db_files:
            print(f"      - {f}")
        results['db_files'] = False
    
    # ============================================
    # 5. Required Packages
    # ============================================
    print("\n📦 Проверка установленных пакетов...")
    total_checks += 1
    
    required_packages = {
        'fastapi': 'Web framework',
        'uvicorn': 'ASGI server',
        'sqlalchemy': 'ORM',
        'pydantic': 'Data validation',
        'pydantic_settings': 'Settings management',
        'aiogram': 'Telegram bot',
        'apscheduler': 'Task scheduler',
        'python-dotenv': 'Environment variables',
        'passlib': 'Password hashing',
        'python-jose': 'JWT tokens'
    }
    
    missing_packages = []
    installed_packages = []
    
    for package, description in required_packages.items():
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            elif package == 'python-jose':
                __import__('jose')
            else:
                __import__(package)
            installed_packages.append(package)
        except ImportError:
            missing_packages.append(f"{package} ({description})")
    
    if not missing_packages:
        print(f"   ✓ Все {len(required_packages)} пакетов установлены")
        results['packages'] = True
        passed_checks += 1
    else:
        print(f"   ✗ Не установлены ({len(missing_packages)}):")
        for p in missing_packages:
            print(f"      - {p}")
        print(f"\n   💡 Установите: pip install -r requirements.txt")
        results['packages'] = False
    
    # ============================================
    # 6. Environment File
    # ============================================
    print("\n🔐 Проверка .env файла...")
    total_checks += 1
    
    if os.path.exists('.env'):
        print("   ✓ Файл .env существует")
        
        # Проверка обязательных переменных
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            required_vars = [
                'DATABASE_PATH',
                'JWT_SECRET_KEY',
                'TELEGRAM_BOT_TOKEN'
            ]
            
            missing_vars = []
            for var in required_vars:
                value = os.getenv(var)
                if not value or 'CHANGE_THIS' in value or 'YOUR_BOT_TOKEN' in value:
                    missing_vars.append(var)
            
            if not missing_vars:
                print("   ✓ Все обязательные переменные заполнены")
                results['env_file'] = True
                passed_checks += 1
            else:
                print(f"   ⚠️  Не заполнены переменные:")
                for v in missing_vars:
                    print(f"      - {v}")
                print("   💡 Запустите: python generate_env.py")
                results['env_file'] = False
        except ImportError:
            print("   ⚠️  python-dotenv не установлен")
            results['env_file'] = False
    else:
        print("   ✗ Файл .env не найден")
        print("   💡 Запустите: python generate_env.py")
        results['env_file'] = False
    
    # ============================================
    # 7. Database Connection
    # ============================================
    print("\n🔌 Проверка подключения к БД...")
    total_checks += 1
    
    if os.path.exists('database/kkt_services.db'):
        print("   ✓ Файл базы данных существует")
        
        try:
            import sqlite3
            conn = sqlite3.connect('database/kkt_services.db')
            cursor = conn.cursor()
            
            # Проверка таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if tables and len(tables) >= 6:
                print(f"   ✓ Найдено {len(tables)} таблиц")
                
                # Проверка данных
                cursor.execute("SELECT COUNT(*) FROM clients")
                clients_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM deadline_types")
                types_count = cursor.fetchone()[0]
                
                if clients_count > 0 and types_count > 0:
                    print(f"   ✓ Начальные данные загружены")
                    print(f"      - Клиентов: {clients_count}")
                    print(f"      - Типов сроков: {types_count}")
                    results['database'] = True
                    passed_checks += 1
                else:
                    print("   ⚠️  Данные не загружены")
                    print("   💡 Запустите: python database/init_database.py")
                    results['database'] = False
            else:
                print(f"   ⚠️  Мало таблиц ({len(tables)}/6+)")
                print("   💡 Запустите: python database/init_database.py")
                results['database'] = False
            
            conn.close()
        except Exception as e:
            print(f"   ✗ Ошибка подключения: {e}")
            results['database'] = False
    else:
        print("   ✗ База данных не создана")
        print("   💡 Запустите: python database/init_database.py")
        results['database'] = False
    
    # ============================================
    # ИТОГОВЫЙ ОТЧЁТ
    # ============================================
    print("\n" + "=" * 70)
    print(" " * 25 + "ИТОГОВЫЙ ОТЧЁТ")
    print("=" * 70)
    
    print(f"\n📊 Результаты проверки: {passed_checks}/{total_checks}")
    print(f"   Успешно: {passed_checks} ✓")
    print(f"   Провалено: {total_checks - passed_checks} ✗")
    
    percentage = (passed_checks / total_checks) * 100
    print(f"\n📈 Прогресс Фазы 1: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n" + "🎉" * 35)
        print("\n" + " " * 15 + "✅ ФАЗА 1 ЗАВЕРШЕНА!")
        print(" " * 10 + "Готовы переходить к Фазе 2!")
        print("\n" + "🎉" * 35)
    elif percentage >= 80:
        print("\n⚠️  Почти готово! Осталось совсем немного.")
    elif percentage >= 50:
        print("\n⏳ Половина пути пройдена. Продолжайте!")
    else:
        print("\n🔧 Нужно выполнить больше шагов из Фазы 1.")
    
    # Следующие шаги
    print("\n" + "=" * 70)
    print(" " * 22 + "СЛЕДУЮЩИЕ ШАГИ")
    print("=" * 70)
    
    if not results.get('packages', True):
        print("\n1️⃣  Установите зависимости:")
        print("   pip install -r requirements.txt")
    
    if not results.get('env_file', True):
        print("\n2️⃣  Создайте .env файл:")
        print("   python generate_env.py")
    
    if not results.get('database', True):
        print("\n3️⃣  Инициализируйте базу данных:")
        print("   python database/init_database.py")
    
    if percentage == 100:
        print("\n✅ Все проверки пройдены!")
        print("\n📚 Фаза 2: Backend API Development")
        print("   Следующий шаг: Создание SQLAlchemy моделей")
    
    print("\n" + "=" * 70)
    
    return percentage == 100

if __name__ == '__main__':
    try:
        success = test_phase1()
        input("\n\nНажмите Enter для выхода...")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        input("\nНажмите Enter для выхода...")
        sys.exit(1)
