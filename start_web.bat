@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ============================================================
echo ZAPUSK WEB SERVERA (FastAPI + Frontend)
echo ============================================================
echo.

REM Proverka virtualnogo okruzheniya
if not exist "venv_web\Scripts\python.exe" (
    echo OSHIBKA: Virtualnoe okruzhenie ne naydeno!
    echo.
    echo Sozdayte virtualnoe okruzhenie komandoy:
    echo   python -m venv venv_web
    echo   venv_web\Scripts\pip install -r requirements-web.txt
    echo.
    pause
    exit /b 1
)

REM Proverka bazy dannykh
if not exist "database\kkt_services.db" (
    echo VNIMANIE: Baza dannykh ne naydena!
    echo.
    echo Initsializiruyte BD komandoy:
    echo   venv_web\Scripts\python database\init_database.py
    echo.
    set /p init="Initializirovat BD seychas? (y/n): "
    if /i "!init!"=="y" (
        echo.
        echo Initializatsiya bazy dannykh...
        venv_web\Scripts\python database\init_database.py
        if errorlevel 1 (
            echo.
            echo Oshibka pri initializatsii BD
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Zapusk bez BD mozhet privesti k oshibkam!
        pause
    )
)

REM Zapusk servera
echo.
echo Zapusk WEB servera na http://localhost:8000
echo.
echo Dostupnye URL:
echo   * Vhod:        http://localhost:8000/login.html
echo   * Dashboard:   http://localhost:8000/dashboard.html
echo   * API Docs:    http://localhost:8000/api/docs
echo   * ReDoc:       http://localhost:8000/api/redoc
echo.
echo Dlya ostanovki nazhmite Ctrl+C
echo.
echo ============================================================
echo.

REM Zapusk uvicorn s avtoperezagruzkoy
venv_web\Scripts\python -m uvicorn web.app.main:app --host 127.0.0.1 --port 8000 --reload

REM Obrabotka oshibok
if errorlevel 1 (
    echo.
    echo ============================================================
    echo OSHIBKA PRI ZAPUSKE SERVERA
    echo ============================================================
    echo.
    echo Vozmozhnye prichiny:
    echo   1. Port 8000 uzhe zanyat drugim protsessom
    echo   2. Otsutstvuyut zavisimosti (requirements-web.txt)
    echo   3. Oshibka v konfiguratsii
    echo.
    echo Poprobujte:
    echo   * Zakryt drugie prilozheniya na portu 8000
    echo   * Pereustanovit zavisimosti:
    echo     venv_web\Scripts\pip install -r requirements-web.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SERVER OSTANOVLEN
echo ============================================================
pause
