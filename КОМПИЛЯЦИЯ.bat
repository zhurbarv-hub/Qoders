@echo off
chcp 65001 >nul
cls
echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                              ║
echo ║                    КОМПИЛЯЦИЯ ПРОЕКТА SERVICETRACKER                         ║
echo ║                                                                              ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.
echo 📋 Этот скрипт скомпилирует проект в .exe файлы
echo.
echo ⚠️  ТРЕБОВАНИЯ:
echo    • Python 3.6 или выше должен быть установлен
echo    • PyInstaller (устанавливается автоматически)
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo.

REM Проверка наличия Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Python не найден!
    echo.
    echo 💡 Установите Python с сайта: https://www.python.org/downloads/
    echo    ВАЖНО: При установке отметьте галочку "Add Python to PATH"
    echo.
    goto :error
)

echo ✅ Python найден
python --version
echo.

REM Проверка PyInstaller
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PyInstaller не установлен
    echo 📦 Устанавливаю PyInstaller...
    echo.
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌ Ошибка установки PyInstaller
        goto :error
    )
    echo ✅ PyInstaller успешно установлен
    echo.
) else (
    echo ✅ PyInstaller уже установлен
    echo.
)

echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo 🔨 НАЧИНАЮ КОМПИЛЯЦИЮ...
echo.

REM Запуск скрипта компиляции
python build.py

if %errorlevel% equ 0 (
    echo.
    echo ════════════════════════════════════════════════════════════════════════════════
    echo.
    echo ✨ КОМПИЛЯЦИЯ ЗАВЕРШЕНА УСПЕШНО! ✨
    echo.
    echo 📁 Скомпилированные файлы находятся в папке: dist\
    echo.
    echo 🚀 Доступные файлы:
    echo    • dist\ServiceTracker_Demo.exe  - Демонстрация системы
    echo    • dist\ServiceTracker_Test.exe  - Тестирование системы
    echo.
    echo 💡 Для удобного запуска используйте:
    echo    • Запуск_Демонстрации.bat
    echo    • Запуск_Тестов.bat
    echo.
    echo ════════════════════════════════════════════════════════════════════════════════
) else (
    echo.
    echo ❌ ОШИБКА КОМПИЛЯЦИИ
    echo.
    echo 💡 Попробуйте:
    echo    1. Обновить PyInstaller: pip install --upgrade pyinstaller
    echo    2. Проверить наличие файла schema.sql
    echo    3. Посмотреть детали в BUILD_INSTRUCTIONS.md
    echo.
)

goto :end

:error
echo.
echo ════════════════════════════════════════════════════════════════════════════════
echo.
echo 📖 Подробные инструкции смотрите в файле: BUILD_INSTRUCTIONS.md
echo.

:end
echo.
pause
