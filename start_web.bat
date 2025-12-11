@echo off
echo ========================================
echo   KKT Web Interface Starter
echo ========================================
echo.

REM Активация виртуального окружения
call venv_web\Scripts\activate.bat

REM Переход в директорию web
cd web

REM Установка PYTHONPATH
set PYTHONPATH=%CD%

echo Starting FastAPI server...
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/api/docs
echo.

REM Запуск сервера
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause