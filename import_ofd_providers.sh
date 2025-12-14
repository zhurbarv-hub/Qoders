#!/bin/bash
# Импорт полного списка операторов ОФД в PostgreSQL на VDS

echo "Импорт операторов ОФД в базу данных kkt_production..."
sudo -u postgres psql -d kkt_production -f /home/kktapp/kkt-system/insert_all_ofd_providers.sql

if [ $? -eq 0 ]; then
    echo "✅ Операторы ОФД успешно импортированы!"
    echo "Проверка количества записей:"
    sudo -u postgres psql -d kkt_production -c "SELECT COUNT(*) as total_providers FROM ofd_providers WHERE is_active = true;"
    echo ""
    echo "Список всех активных операторов:"
    sudo -u postgres psql -d kkt_production -c "SELECT id, name, support_phone FROM ofd_providers WHERE is_active = true ORDER BY name;"
else
    echo "❌ Ошибка при импорте операторов ОФД"
    exit 1
fi
