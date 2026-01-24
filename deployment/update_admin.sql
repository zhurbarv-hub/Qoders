-- ============================================
-- Обновление администратора после развертывания
-- ============================================

-- Обновляем Telegram ID администратора
UPDATE users 
SET telegram_id = '5064340711',
    telegram_username = NULL,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 1 OR email = 'admin@kkt-system.ru';

-- Проверяем результат
SELECT id, email, full_name, role, telegram_id, is_active 
FROM users 
WHERE id = 1;

-- Вывод для подтверждения
SELECT 'Администратор обновлен успешно' as status,
       email,
       telegram_id
FROM users 
WHERE id = 1;
