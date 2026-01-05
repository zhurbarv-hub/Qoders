#!/bin/bash
# Проверка касс на VDS

echo "=== Проверка касс в БД ==="
echo ""

echo "1️⃣ Всего касс:"
ssh root@185.185.71.248 'psql -U kkt_user -d kkt_production -t -c "SELECT COUNT(*) FROM cash_registers;"'

echo ""
echo "2️⃣ Активных касс:"
ssh root@185.185.71.248 'psql -U kkt_user -d kkt_production -t -c "SELECT COUNT(*) FROM cash_registers WHERE is_active = true;"'

echo ""
echo "3️⃣ Список касс с клиентами:"
ssh root@185.185.71.248 'psql -U kkt_user -d kkt_production -c "SELECT cr.id, cr.register_name, cr.model, cr.is_active, u.company_name FROM cash_registers cr JOIN users u ON cr.client_id = u.id ORDER BY cr.id LIMIT 10;"'
