-- ============================================
-- KKT Services Expiration Management System
-- Database Schema v1.0
-- ============================================

-- Drop existing tables if recreating (осторожно!)
DROP TABLE IF EXISTS notification_logs;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS deadlines;
DROP TABLE IF EXISTS deadline_types;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS users;

-- ============================================
-- Таблица: Пользователи (Администраторы)
-- ============================================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- ============================================
-- Таблица: Клиенты
-- ============================================
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    inn VARCHAR(12) NOT NULL UNIQUE,
    contact_person VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_inn_length CHECK (length(inn) IN (10, 12))
);

CREATE INDEX idx_clients_inn ON clients(inn);
CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_active ON clients(is_active);

-- ============================================
-- Таблица: Типы сроков (услуг)
-- ============================================
CREATE TABLE deadline_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_system BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deadline_types_active ON deadline_types(is_active);

-- ============================================
-- Таблица: Сроки истечения услуг
-- ============================================
CREATE TABLE deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    deadline_type_id INTEGER NOT NULL,
    expiration_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (deadline_type_id) REFERENCES deadline_types(id)
);

CREATE INDEX idx_deadlines_client ON deadlines(client_id);
CREATE INDEX idx_deadlines_expiration ON deadlines(expiration_date);
CREATE INDEX idx_deadlines_status ON deadlines(status);
CREATE INDEX idx_deadlines_type ON deadlines(deadline_type_id);

-- ============================================
-- Таблица: Telegram контакты
-- ============================================
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    telegram_id VARCHAR(50) NOT NULL UNIQUE,
    telegram_username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    notifications_enabled BOOLEAN DEFAULT 1,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deadline_id INTEGER NOT NULL,
    recipient_telegram_id VARCHAR(50) NOT NULL,
    message_text TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'sent',
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
    c.name AS client_name,
    c.inn AS client_inn,
    dt.type_name AS deadline_type_name,
    d.expiration_date,
    CAST((julianday(d.expiration_date) - julianday('now')) AS INTEGER) AS days_until_expiration,
    CASE 
        WHEN julianday(d.expiration_date) - julianday('now') < 0 THEN 'expired'
        WHEN julianday(d.expiration_date) - julianday('now') < 7 THEN 'red'
        WHEN julianday(d.expiration_date) - julianday('now') < 14 THEN 'yellow'
        ELSE 'green'
    END AS status_color,
    d.status,
    d.notes,
    ct.telegram_id AS contact_telegram_id,
    ct.telegram_username AS contact_telegram_username,
    ct.notifications_enabled
FROM deadlines d
INNER JOIN clients c ON d.client_id = c.id
INNER JOIN deadline_types dt ON d.deadline_type_id = dt.id
LEFT JOIN contacts ct ON c.id = ct.client_id
WHERE d.status = 'active' AND c.is_active = 1;

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
    COUNT(DISTINCT CASE WHEN c.is_active = 1 THEN c.id END) AS active_clients,
    COUNT(d.id) AS total_deadlines,
    COUNT(CASE WHEN d.status = 'active' THEN 1 END) AS active_deadlines,
    COUNT(CASE WHEN julianday(d.expiration_date) - julianday('now') > 14 THEN 1 END) AS status_green,
    COUNT(CASE WHEN julianday(d.expiration_date) - julianday('now') BETWEEN 7 AND 14 THEN 1 END) AS status_yellow,
    COUNT(CASE WHEN julianday(d.expiration_date) - julianday('now') BETWEEN 0 AND 7 THEN 1 END) AS status_red,
    COUNT(CASE WHEN julianday(d.expiration_date) - julianday('now') < 0 THEN 1 END) AS status_expired
FROM clients c
LEFT JOIN deadlines d ON c.id = d.client_id;