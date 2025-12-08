-- ============================================
-- Начальные данные для системы KKT
-- ============================================

-- Типы сроков (предустановленные)
INSERT INTO deadline_types (type_name, description, is_system, is_active) VALUES
('OFD', 'Оператор Фискальных Данных - сервис передачи фискальных данных', 1, 1),
('KKT Registration', 'Регистрация ККТ в налоговой службе', 1, 1),
('Software License', 'Лицензия на программное обеспечение ККТ', 1, 1),
('Technical Support', 'Техническая поддержка оборудования', 1, 1),
('EKLZ', 'Электронная контрольная лента защищённая', 1, 1),
('Network Service', 'Сетевое обслуживание и связь', 1, 1),
('Cloud Storage', 'Облачное хранилище данных', 1, 1);

-- Администратор по умолчанию
-- Email: admin@kkt.local
-- Password: admin123
-- ⚠️ ВАЖНО: Измените пароль после первого входа!
INSERT INTO users (email, password_hash, full_name, role, is_active) VALUES
('admin@kkt.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5uf0z.n82oB5K', 'Системный Администратор', 'admin', 1);

-- Тестовые клиенты
INSERT INTO clients (name, inn, contact_person, phone, email, is_active) VALUES
('ООО "Ромашка"', '7701234567', 'Иванов Иван Иванович', '+79161234567', 'ivanov@romashka.ru', 1),
('ИП Петров П.П.', '123456789012', 'Петров Пётр Петрович', '+79169876543', 'petrov@mail.ru', 1),
('ООО "Торговый Дом"', '7702345678', 'Сидорова Анна Сергеевна', '+79165554433', 'sidorova@td.ru', 1);

-- Тестовые сроки
INSERT INTO deadlines (client_id, deadline_type_id, expiration_date, status, notes) VALUES
(1, 1, date('now', '+45 days'), 'active', 'Ежегодное продление договора с ОФД'),
(1, 2, date('now', '+120 days'), 'active', 'Плановая перерегистрация'),
(2, 1, date('now', '+10 days'), 'active', 'СРОЧНО! Скоро истекает'),
(2, 3, date('now', '+5 days'), 'active', 'КРИТИЧНО! Обновить лицензию'),
(3, 4, date('now', '+60 days'), 'active', 'Продление тех. поддержки'),
(3, 6, date('now', '+90 days'), 'active', 'Оплата сетевых услуг');

-- Тестовый контакт (замените на реальный Telegram ID при тестировании)
INSERT INTO contacts (client_id, telegram_id, telegram_username, first_name, notifications_enabled) VALUES
(1, '123456789', 'ivan_test', 'Иван', 1);

-- ============================================
-- Проверочные запросы
-- ============================================

SELECT '=== ТИПЫ СРОКОВ ===' AS info;
SELECT id, type_name, description FROM deadline_types;

SELECT '=== ПОЛЬЗОВАТЕЛИ ===' AS info;
SELECT id, email, full_name, role FROM users;

SELECT '=== КЛИЕНТЫ ===' AS info;
SELECT id, name, inn, contact_person FROM clients;

SELECT '=== СРОКИ (с деталями) ===' AS info;
SELECT 
    client_name, 
    deadline_type_name, 
    expiration_date, 
    days_until_expiration, 
    status_color 
FROM v_active_deadlines_with_details;

SELECT '=== СТАТИСТИКА ===' AS info;
SELECT * FROM v_dashboard_stats;
