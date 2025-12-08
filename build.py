"""
Скрипт для компиляции проекта в исполняемые файлы
"""

import os
import sys
import shutil
import subprocess


def check_pyinstaller():
    """Проверка установки PyInstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller установлен")
        return True
    except ImportError:
        print("❌ PyInstaller не установлен")
        print("\n📦 Устанавливаю PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller успешно установлен")
            return True
        except Exception as e:
            print(f"❌ Ошибка установки PyInstaller: {e}")
            return False


def clean_build_dirs():
    """Очистка директорий сборки"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Очистка {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Удаляем .spec файлы
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            os.remove(file)
            print(f"🧹 Удален {file}")


def build_executable(script_name, exe_name, icon=None, onefile=True):
    """
    Компилирует Python скрипт в исполняемый файл
    
    Args:
        script_name: имя Python скрипта
        exe_name: имя выходного exe файла
        icon: путь к иконке (опционально)
        onefile: создать один файл (True) или директорию (False)
    """
    print(f"\n{'='*70}")
    print(f"🔨 Компиляция: {script_name} -> {exe_name}.exe")
    print(f"{'='*70}")
    
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        f'--name={exe_name}',
    ]
    
    if onefile:
        cmd.append('--onefile')
    
    # Добавляем schema.sql как дополнительный файл
    cmd.extend(['--add-data', 'schema.sql;.'])
    
    # Консольное приложение
    cmd.append('--console')
    
    # Скрываем импорты
    cmd.extend(['--hidden-import', 'sqlite3'])
    
    if icon and os.path.exists(icon):
        cmd.extend(['--icon', icon])
    
    cmd.append(script_name)
    
    try:
        print(f"\n🔧 Команда: {' '.join(cmd)}\n")
        subprocess.check_call(cmd)
        print(f"\n✅ Успешно создан: dist/{exe_name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка компиляции: {e}")
        return False


def create_batch_files():
    """Создает batch файлы для удобного запуска"""
    
    # Batch файл для запуска демонстрации
    demo_bat = """@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                   ДЕМОНСТРАЦИЯ СИСТЕМЫ ОТСЛЕЖИВАНИЯ СЕРВИСОВ                 ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
ServiceTracker_Demo.exe
pause
"""
    
    with open('Запуск_Демонстрации.bat', 'w', encoding='utf-8') as f:
        f.write(demo_bat)
    
    # Batch файл для запуска тестов
    test_bat = """@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                        ТЕСТИРОВАНИЕ СИСТЕМЫ                                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
ServiceTracker_Test.exe
pause
"""
    
    with open('Запуск_Тестов.bat', 'w', encoding='utf-8') as f:
        f.write(test_bat)
    
    print("\n✅ Созданы batch файлы:")
    print("   - Запуск_Демонстрации.bat")
    print("   - Запуск_Тестов.bat")


def copy_schema_to_dist():
    """Копирует schema.sql в dist директорию"""
    if os.path.exists('dist'):
        shutil.copy('schema.sql', 'dist/schema.sql')
        print("✅ Скопирован schema.sql в dist/")


def main():
    """Основная функция сборки"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    КОМПИЛЯЦИЯ ПРОЕКТА SERVICETRACKER                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Проверка PyInstaller
    if not check_pyinstaller():
        print("\n❌ Невозможно продолжить без PyInstaller")
        return False
    
    print("\n" + "="*70)
    choice = input("\n🧹 Очистить старые файлы сборки? (y/n): ").strip().lower()
    if choice == 'y':
        clean_build_dirs()
    
    success_count = 0
    total_count = 2
    
    # Компиляция демонстрационного примера
    if build_executable('example_usage.py', 'ServiceTracker_Demo', onefile=True):
        success_count += 1
    
    # Компиляция тестов
    if build_executable('test_system.py', 'ServiceTracker_Test', onefile=True):
        success_count += 1
    
    # Копируем schema.sql
    copy_schema_to_dist()
    
    # Создаем batch файлы
    create_batch_files()
    
    # Итоговая информация
    print("\n" + "="*70)
    print(f"\n📊 РЕЗУЛЬТАТЫ КОМПИЛЯЦИИ: {success_count}/{total_count} успешно")
    print("="*70)
    
    if success_count == total_count:
        print("\n✨ ВСЕ ФАЙЛЫ УСПЕШНО СКОМПИЛИРОВАНЫ! ✨\n")
        print("📁 Скомпилированные файлы находятся в директории: dist/\n")
        print("🚀 Доступные исполняемые файлы:")
        print("   • ServiceTracker_Demo.exe  - полная демонстрация системы")
        print("   • ServiceTracker_Test.exe  - тестирование системы")
        print("\n💡 Для удобства используйте batch файлы:")
        print("   • Запуск_Демонстрации.bat")
        print("   • Запуск_Тестов.bat")
        
        print("\n" + "="*70)
        print("\n📦 Содержимое dist/ готово к распространению:")
        print("   - Скопируйте всю папку dist/ на другой компьютер")
        print("   - Запускайте .exe файлы без установки Python")
        print("="*70)
        
        return True
    else:
        print("\n⚠️ Некоторые файлы не удалось скомпилировать")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Сборка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
