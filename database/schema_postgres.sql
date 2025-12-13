-- ============================================
-- KKT Services Expiration Management System
-- PostgreSQL Database Schema v1.0
-- Adapted from SQLite schema for production deployment
-- ============================================

-- Drop existing tables if recreating (осторожно!)
DROP TABLE IF EXISTS notification_logs CASCADE;
DROP TABLE IF EXISTS cash_registers CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS deadlines CASCADE;
DROP TABLE IF EXISTS deadline_types CASCADE;
DROP TABLE IF EXISTS ofd_providers CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- Таблица: Пользователи (Администраторы и поддержка)
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'admin' CHECK (role IN ('admin', 'manager', 'support', 'client')),
    is_active BOOLEAN DEFAULT TRUE,
    telegram_id VARCHAR(50) UNIQUE,
    telegram_username VARCHAR(100),
    registration_code VARCHAR(10),
    code_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_telegram ON users(telegram_id);
CREATE INDEX idx_users_role ON users(role);

-- ============================================
-- Таблица: ОФД провайдеры
-- ============================================
CREATE TABLE ofd_providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    full_name TEXT,
    website VARCHAR(255),
    support_phone VARCHAR(50),
    support_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ofd_providers_active ON ofd_providers(is_active);

-- ============================================
-- Таблица: Клиенты
-- ============================================
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    inn VARCHAR(12) NOT NULL UNIQUE,
    contact_person VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_inn_length CHECK (char_length(inn) IN (10, 12))
);

CREATE INDEX idx_clients_inn ON clients(inn);
CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_active ON clients(is_active);

-- ============================================
-- Таблица: Типы сроков (услуг)
-- ============================================
CREATE TABLE deadline_types (
    id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deadline_types_active ON deadline_types(is_active);
CREATE INDEX idx_deadline_types_system ON deadline_types(is_system);

-- ============================================
-- Таблица: Кассовые аппараты
-- ============================================
CREATE TABLE cash_registers (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    serial_number VARCHAR(50) NOT NULL,
    model VARCHAR(100),
    registration_number VARCHAR(50),
    fiscal_storage_number VARCHAR(50),
    ofd_provider_id INTEGER,
    ofd_contract_number VARCHAR(100),
    ofd_contract_date DATE,
    ofd_notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (ofd_provider_id) REFERENCES ofd_providers(id) ON DELETE SET NULL,
    CONSTRAINT unique_serial_per_client UNIQUE (client_id, serial_number)
);

CREATE INDEX idx_cash_registers_client ON cash_registers(client_id);
CREATE INDEX idx_cash_registers_serial ON cash_registers(serial_number);
CREATE INDEX idx_cash_registers_active ON cash_registers(is_active);
CREATE INDEX idx_cash_registers_ofd ON cash_registers(ofd_provider_id);

-- ============================================
-- Таблица: Сроки истечения услуг
-- ============================================
CREATE TABLE deadlines (
    id SERIAL PRIMARY KEY,
    client_id INTEGER,
    cash_register_id INTEGER,
    deadline_type_id INTEGER NOT NULL,
    expiration_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'renewed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (cash_register_id) REFERENCES cash_registers(id) ON DELETE CASCADE,
    FOREIGN KEY (deadline_type_id) REFERENCES deadline_types(id) ON DELETE RESTRICT,
    CONSTRAINT check_client_or_cash_register CHECK (
        (client_id IS NOT NULL AND cash_register_id IS NULL) OR
        (client_id IS NULL AND cash_register_id IS NOT NULL)
    )
);

CREATE INDEX idx_deadlines_client ON deadlines(client_id);
CREATE INDEX idx_deadlines_cash_register ON deadlines(cash_register_id);
CREATE INDEX idx_deadlines_expiration ON deadlines(expiration_date);
CREATE INDEX idx_deadlines_status ON deadlines(status);
CREATE INDEX idx_deadlines_type ON deadlines(deadline_type_id);

-- ============================================
-- Таблица: Telegram контакты
-- ============================================
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL,
    telegram_id VARCHAR(50) NOT NULL UNIQUE,
    telegram_username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    notifications_enabled BOOLEAN DEFAULT TRUE,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP,
    
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE INDEX idx_contacts_client ON contacts(client_id);
CREATE INDEX idx_contacts_telegram ON contacts(telegram_id);
CREATE INDEX idx_contacts_enabled ON contacts(notifications_enabled);

-- ============================================
-- Таблица: Логи уведомлений
-- ============================================
CREATE TABLE notification_logs (
    id SERIAL PRIMARY KEY,
    deadline_id INTEGER NOT NULL,
    recipient_telegram_id VARCHAR(50) NOT NULL,
    message_text TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'pending')),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    
    FOREIGN KEY (deadline_id) REFERENCES deadlines(id) ON DELETE CASCADE
);

CREATE INDEX idx_notification_logs_deadline ON notification_logs(deadline_id);
CREATE INDEX idx_notification_logs_sent ON notification_logs(sent_at);
CREATE INDEX idx_notification_logs_status ON notification_logs(status);

-- ============================================
-- ПРЕДСТАВЛЕНИЯ (VIEWS)
-- ============================================

-- Активные сроки с полной информацией
CREATE VIEW v_active_deadlines_with_details AS
SELECT 
    d.id AS deadline_id,
    d.client_id,
    d.cash_register_id,
    c.name AS client_name,
    c.inn AS client_inn,
    cr.serial_number AS cash_register_serial,
    cr.model AS cash_register_model,
    dt.type_name AS deadline_type_name,
    d.expiration_date,
    (d.expiration_date - CURRENT_DATE) AS days_until_expiration,
    CASE 
        WHEN (d.expiration_date - CURRENT_DATE) < 0 THEN 'expired'
        WHEN (d.expiration_date - CURRENT_DATE) < 7 THEN 'red'
        WHEN (d.expiration_date - CURRENT_DATE) < 14 THEN 'yellow'
        ELSE 'green'
    END AS status_color,
    d.status,
    d.notes,
    ct.telegram_id AS contact_telegram_id,
    ct.telegram_username AS contact_telegram_username,
    ct.notifications_enabled
FROM deadlines d
LEFT JOIN clients c ON d.client_id = c.id
LEFT JOIN cash_registers cr ON d.cash_register_id = cr.id
INNER JOIN deadline_types dt ON d.deadline_type_id = dt.id
LEFT JOIN contacts ct ON c.id = ct.client_id OR cr.client_id = ct.client_id
WHERE d.status = 'active' AND (c.is_active = TRUE OR cr.is_active = TRUE);

-- Скоро истекающие (в течение 14 дней)
CREATE VIEW v_expiring_soon AS
SELECT *
FROM v_active_deadlines_with_details
WHERE days_until_expiration <= 14 AND days_until_expiration >= 0
ORDER BY days_until_expiration ASC;

-- Статистика для дашборда
CREATE VIEW v_dashboard_stats AS
SELECT 
    COUNT(DISTINCT c.id) AS total_clients,
    COUNT(DISTINCT CASE WHEN c.is_active = TRUE THEN c.id END) AS active_clients,
    COUNT(d.id) AS total_deadlines,
    COUNT(CASE WHEN d.status = 'active' THEN 1 END) AS active_deadlines,
    COUNT(CASE WHEN (d.expiration_date - CURRENT_DATE) > 14 THEN 1 END) AS status_green,
    COUNT(CASE WHEN (d.expiration_date - CURRENT_DATE) BETWEEN 7 AND 14 THEN 1 END) AS status_yellow,
    COUNT(CASE WHEN (d.expiration_date - CURRENT_DATE) BETWEEN 0 AND 7 THEN 1 END) AS status_red,
    COUNT(CASE WHEN (d.expiration_date - CURRENT_DATE) < 0 THEN 1 END) AS status_expired
FROM clients c
LEFT JOIN deadlines d ON c.id = d.client_id;

-- ============================================
-- Начальные данные
-- ============================================

-- Типы дедлайнов
INSERT INTO deadline_types (type_name, description, is_system) VALUES
('ОФД', 'Срок действия договора с ОФД', FALSE),
('Регистрация ККТ', 'Дата окончания регистрации ККТ в ФНС', FALSE),
('ФН (Фискальный накопитель)', 'Срок действия фискального накопителя', FALSE),
('Техническое обслуживание', 'Плановое ТО кассового аппарата', FALSE);

-- Администратор по умолчанию (пароль: admin123)
-- Хеш сгенерирован с помощью bcrypt
INSERT INTO users (email, password_hash, full_name, role, is_active) VALUES
('admin@kkt-system.ru', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ND2fxqC0PZEy', 'Администратор системы', 'admin', TRUE);

-- ============================================
-- Комментарии
-- ============================================

COMMENT ON TABLE users IS 'Пользователи системы (администраторы, менеджеры, клиенты)';
COMMENT ON TABLE clients IS 'Организации-клиенты';
COMMENT ON TABLE deadline_types IS 'Типы услуг с дедлайнами';
COMMENT ON TABLE deadlines IS 'Сроки истечения услуг для клиентов и ККТ';
COMMENT ON TABLE contacts IS 'Telegram контакты для уведомлений';
COMMENT ON TABLE notification_logs IS 'История отправленных уведомлений';
COMMENT ON TABLE cash_registers IS 'Кассовые аппараты клиентов';
COMMENT ON TABLE ofd_providers IS 'Операторы фискальных данных';

COMMENT ON COLUMN users.role IS 'Роль: admin, manager, support, client';
COMMENT ON COLUMN deadlines.status IS 'Статус: active, expired, renewed, cancelled';
COMMENT ON COLUMN deadlines.client_id IS 'ID клиента (для общих дедлайнов)';
COMMENT ON COLUMN deadlines.cash_register_id IS 'ID ККТ (для дедлайнов конкретной кассы)';
