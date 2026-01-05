@echo off
REM Скрипт для загрузки обновленных файлов на VDS и применения миграции

echo ================================================
echo Загрузка обновленных файлов на VDS
echo ================================================

set VDS_HOST=root@185.185.71.248
set VDS_PATH=/opt/kkt/web

echo.
echo [1/5] Загрузка миграции SQL...
echo 7ywyrfrweitkws_bmm8k | pscp -pw 7ywyrfrweitkws_bmm8k web\app\migrations\010_add_cash_register_name_and_address.sql %VDS_HOST%:%VDS_PATH%/app/migrations/

echo.
echo [2/5] Загрузка обновленной модели cash_register.py...
echo 7ywyrfrweitkws_bmm8k | pscp -pw 7ywyrfrweitkws_bmm8k web\app\models\cash_register.py %VDS_HOST%:%VDS_PATH%/app/models/

echo.
echo [3/5] Загрузка обновленного API cash_registers.py...
echo 7ywyrfrweitkws_bmm8k | pscp -pw 7ywyrfrweitkws_bmm8k web\app\api\cash_registers.py %VDS_HOST%:%VDS_PATH%/app/api/

echo.
echo [4/5] Загрузка обновленного client-details.js...
echo 7ywyrfrweitkws_bmm8k | pscp -pw 7ywyrfrweitkws_bmm8k web\app\static\js\client-details.js %VDS_HOST%:%VDS_PATH%/app/static/js/

echo.
echo [5/5] Загрузка скрипта применения миграции...
echo 7ywyrfrweitkws_bmm8k | pscp -pw 7ywyrfrweitkws_bmm8k web\apply_migration_010.py %VDS_HOST%:%VDS_PATH%/

echo.
echo ================================================
echo Применение миграции на VDS
echo ================================================
echo 7ywyrfrweitkws_bmm8k | plink -pw 7ywyrfrweitkws_bmm8k %VDS_HOST% "cd /opt/kkt/web && python3 apply_migration_010.py"

echo.
echo ================================================
echo Перезапуск web-сервиса
echo ================================================
echo 7ywyrfrweitkws_bmm8k | plink -pw 7ywyrfrweitkws_bmm8k %VDS_HOST% "systemctl restart kkt-web"
echo 7ywyrfrweitkws_bmm8k | plink -pw 7ywyrfrweitkws_bmm8k %VDS_HOST% "systemctl status kkt-web --no-pager"

echo.
echo ================================================
echo Готово! Проверьте работу на https://kkt-box.net
echo ================================================
pause
