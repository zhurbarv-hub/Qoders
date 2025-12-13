@echo off
chcp 65001 >nul
echo ======================================================================
echo RESTART WEB SERVER
echo ======================================================================
echo.

echo [1/3] Stopping current server...
taskkill /F /IM uvicorn.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Server stopped
) else (
    echo    [INFO] Server was not running
)

echo.
echo [2/3] Waiting for process to terminate...
timeout /t 2 /nobreak >nul

echo.
echo [3/3] Starting server in new window...
start "KKT Web Server" cmd /k "cd /d "%~dp0" && start_web.bat"

echo.
echo ======================================================================
echo [SUCCESS] Web server restarted!
echo ======================================================================
echo.
echo Next steps:
echo 1. Open http://localhost:8000/static/dashboard.html
echo 2. Go to Clients section
echo 3. Open any client card
echo 4. Edit OFD renewal date in any cash register
echo 5. Save changes
echo 6. Check that deadline was created automatically
echo ======================================================================
echo.
pause
