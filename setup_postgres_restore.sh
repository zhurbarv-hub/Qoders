#!/bin/bash
# Установка пароля для postgres и тест восстановления

POSTGRES_PASSWORD="PostgresSecure2024KKT"

echo "=== УСТАНОВКА ПАРОЛЯ POSTGRES ==="
sudo -u postgres psql <<EOF
ALTER USER postgres WITH PASSWORD '$POSTGRES_PASSWORD';
\q
EOF

echo ""
echo "✅ Пароль установлен"
echo ""
echo "=== ТЕСТ ВОССТАНОВЛЕНИЯ С POSTGRES ==="

BACKUP="/home/kktapp/kkt-system/backups/database/kkt_test_backup.sql"

if [ ! -f "$BACKUP" ]; then
    echo "❌ Файл бэкапа не найден"
    exit 1
fi

echo "📊 Размер бэкапа: $(du -h "$BACKUP" | cut -f1)"
echo "🔄 Запуск восстановления..."

START=$(date +%s)

PGPASSWORD="$POSTGRES_PASSWORD" psql \
    -h localhost \
    -p 5432 \
    -U postgres \
    -d kkt_production \
    -f "$BACKUP" \
    --single-transaction \
    --set ON_ERROR_STOP=on \
    -v ON_ERROR_STOP=1 \
    -q

EXIT_CODE=$?
END=$(date +%s)
ELAPSED=$((END - START))

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ УСПЕХ! Восстановление завершено за ${ELAPSED} сек"
    echo ""
    echo "Пароль postgres сохранён: $POSTGRES_PASSWORD"
else
    echo "❌ Ошибка (код: $EXIT_CODE)"
    exit 1
fi
