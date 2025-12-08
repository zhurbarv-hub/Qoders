@echo off
REM Start KKT Services Backend API Server
REM This script starts the FastAPI backend server with auto-reload for development

echo ========================================
echo KKT SERVICES BACKEND API SERVER
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Please create .env file with required configuration
    echo You can copy from .env.example
    pause
    exit /b 1
)

echo [INFO] Starting FastAPI server...
echo [INFO] API Documentation: http://localhost:8000/docs
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Start FastAPI server with uvicorn
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
