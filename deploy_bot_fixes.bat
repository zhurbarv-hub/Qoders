@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 ДЕПЛОЙ ИСПРАВЛЕНИЙ TELEGRAM БОТА
echo ============================================================
echo.

set VDS_HOST=185.185.71.248
set VDS_PORT=40022
set VDS_USER=root

echo 📤 Копирование файлов на VDS...
echo.

echo   📄 notifier.py
C:\Windows\System32\OpenSSH\scp.exe -P %VDS_PORT% "d:\QoProj\KKT\bot\services\notifier.py" %VDS_USER%@%VDS_HOST%:/root/kkt_system/bot/services/notifier.py
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Скопировано!
) else (
    echo   ⚠️ Ошибка копирования notifier.py
)
echo.

echo   📄 formatter.py
C:\Windows\System32\OpenSSH\scp.exe -P %VDS_PORT% "d:\QoProj\KKT\bot\services\formatter.py" %VDS_USER%@%VDS_HOST%:/root/kkt_system/bot/services/formatter.py
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Скопировано!
) else (
    echo   ⚠️ Ошибка копирования formatter.py
)
echo.

echo 🔄 Перезапуск Telegram бота...
C:\Windows\System32\OpenSSH\ssh.exe -p %VDS_PORT% %VDS_USER%@%VDS_HOST% "systemctl restart kkt_bot"
if %ERRORLEVEL% EQU 0 (
    echo ✅ Бот перезапущен!
) else (
    echo ⚠️ Ошибка перезапуска
)
echo.

echo 📊 Статус бота:
C:\Windows\System32\OpenSSH\ssh.exe -p %VDS_PORT% %VDS_USER%@%VDS_HOST% "systemctl is-active kkt_bot"
echo.

echo ============================================================
echo ✅ ДЕПЛОЙ ЗАВЕРШЕН
echo ============================================================
echo.
echo 📝 Изменения:
echo   1. Добавлен parse_mode='HTML' в send_notification()
echo   2. Улучшено форматирование уведомлений с детализацией
echo   3. Добавлены уровни срочности и призывы к действию
echo.
echo 🔔 Теперь HTML-теги будут правильно отображаться!
echo.
pause
@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 ДЕПЛОЙ ИСПРАВЛЕНИЙ TELEGRAM БОТА
echo ============================================================
echo.

set VDS_HOST=185.185.71.248
set VDS_PORT=40022
set VDS_USER=root

echo 📤 Копирование файлов на VDS...
echo.

echo   📄 notifier.py
C:\Windows\System32\OpenSSH\scp.exe -P %VDS_PORT% "d:\QoProj\KKT\bot\services\notifier.py" %VDS_USER%@%VDS_HOST%:/root/kkt_system/bot/services/notifier.py
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Скопировано!
) else (
    echo   ⚠️ Ошибка копирования notifier.py
)
echo.

echo   📄 formatter.py
C:\Windows\System32\OpenSSH\scp.exe -P %VDS_PORT% "d:\QoProj\KKT\bot\services\formatter.py" %VDS_USER%@%VDS_HOST%:/root/kkt_system/bot/services/formatter.py
if %ERRORLEVEL% EQU 0 (
    echo   ✅ Скопировано!
) else (
    echo   ⚠️ Ошибка копирования formatter.py
)
echo.

echo 🔄 Перезапуск Telegram бота...
C:\Windows\System32\OpenSSH\ssh.exe -p %VDS_PORT% %VDS_USER%@%VDS_HOST% "systemctl restart kkt_bot"
if %ERRORLEVEL% EQU 0 (
    echo ✅ Бот перезапущен!
) else (
    echo ⚠️ Ошибка перезапуска
)
echo.

echo 📊 Статус бота:
C:\Windows\System32\OpenSSH\ssh.exe -p %VDS_PORT% %VDS_USER%@%VDS_HOST% "systemctl is-active kkt_bot"
echo.

echo ============================================================
echo ✅ ДЕПЛОЙ ЗАВЕРШЕН
echo ============================================================
echo.
echo 📝 Изменения:
echo   1. Добавлен parse_mode='HTML' в send_notification()
echo   2. Улучшено форматирование уведомлений с детализацией
echo   3. Добавлены уровни срочности и призывы к действию
echo.
echo 🔔 Теперь HTML-теги будут правильно отображаться!
echo.
pause
