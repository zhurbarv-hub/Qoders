-- Добавляем тестовые дедлайны для клиентов
INSERT INTO deadlines (user_id, deadline_type_id, expiration_date, status, notes)
SELECT 
    u.id,
    dt.id,
    CURRENT_DATE + INTERVAL '30 days',
    'active',
    'Test deadline - ' || dt.type_name
FROM users u
CROSS JOIN deadline_types dt
WHERE u.role = 'client'
  AND u.is_active = true
LIMIT 10;

-- Показываем результат
SELECT 'Total deadlines:', COUNT(*) FROM deadlines;

-- Показываем детали последних дедлайнов
SELECT 
    d.id,
    u.full_name as client_name,
    dt.type_name as service_type,
    d.expiration_date,
    d.status
FROM deadlines d
JOIN users u ON d.user_id = u.id
JOIN deadline_types dt ON d.deadline_type_id = dt.id
ORDER BY d.created_at DESC
LIMIT 10;
