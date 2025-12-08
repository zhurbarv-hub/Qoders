-- СУБД для фиксации сроков истечения сервисов
-- Создание базы данных и таблиц

-- Таблица для хранения информации о сервисах
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name VARCHAR(255) NOT NULL,
    description TEXT,
    provider VARCHAR(255),
    category VARCHAR(100),
    cost DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'RUB',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    UNIQUE(service_name)
);

-- Таблица для хранения подписок и сроков истечения
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL,
    subscription_type VARCHAR(50), -- monthly, yearly, one-time, etc.
    start_date DATE NOT NULL,
    expiration_date DATE NOT NULL,
    renewal_date DATE,
    auto_renewal BOOLEAN DEFAULT 0,
    notification_days INTEGER DEFAULT 30, -- за сколько дней уведомлять
    status VARCHAR(50) DEFAULT 'active', -- active, expired, cancelled, suspended
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- Таблица для истории платежей
CREATE TABLE IF NOT EXISTS payment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'RUB',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'completed', -- completed, pending, failed, refunded
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);

-- Таблица для уведомлений
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL,
    notification_date DATE NOT NULL,
    notification_type VARCHAR(50), -- expiring_soon, expired, payment_due
    is_sent BOOLEAN DEFAULT 0,
    sent_at TIMESTAMP,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);

-- Индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_services_category ON services(category);
CREATE INDEX IF NOT EXISTS idx_services_active ON services(is_active);
CREATE INDEX IF NOT EXISTS idx_subscriptions_service ON subscriptions(service_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_expiration ON subscriptions(expiration_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_payment_history_subscription ON payment_history(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payment_history_date ON payment_history(payment_date);
CREATE INDEX IF NOT EXISTS idx_notifications_subscription ON notifications(subscription_id);
CREATE INDEX IF NOT EXISTS idx_notifications_date ON notifications(notification_date);
CREATE INDEX IF NOT EXISTS idx_notifications_sent ON notifications(is_sent);

-- Представления для удобства работы

-- Представление активных подписок с информацией о сервисе
CREATE VIEW IF NOT EXISTS v_active_subscriptions AS
SELECT 
    s.id as service_id,
    s.service_name,
    s.provider,
    s.category,
    s.cost,
    s.currency,
    sub.id as subscription_id,
    sub.subscription_type,
    sub.start_date,
    sub.expiration_date,
    sub.renewal_date,
    sub.auto_renewal,
    sub.status,
    sub.notification_days,
    CAST((julianday(sub.expiration_date) - julianday('now')) AS INTEGER) as days_until_expiration
FROM services s
INNER JOIN subscriptions sub ON s.id = sub.service_id
WHERE sub.status = 'active' AND s.is_active = 1;

-- Представление истекающих подписок
CREATE VIEW IF NOT EXISTS v_expiring_subscriptions AS
SELECT 
    s.service_name,
    s.provider,
    sub.expiration_date,
    sub.status,
    CAST((julianday(sub.expiration_date) - julianday('now')) AS INTEGER) as days_until_expiration,
    sub.auto_renewal,
    sub.notification_days
FROM services s
INNER JOIN subscriptions sub ON s.id = sub.service_id
WHERE sub.status = 'active' 
    AND s.is_active = 1
    AND julianday(sub.expiration_date) - julianday('now') <= sub.notification_days
ORDER BY sub.expiration_date ASC;

-- Представление статистики по платежам
CREATE VIEW IF NOT EXISTS v_payment_statistics AS
SELECT 
    s.service_name,
    s.category,
    COUNT(ph.id) as payment_count,
    SUM(ph.amount) as total_paid,
    AVG(ph.amount) as average_payment,
    MIN(ph.payment_date) as first_payment,
    MAX(ph.payment_date) as last_payment
FROM services s
INNER JOIN subscriptions sub ON s.id = sub.service_id
INNER JOIN payment_history ph ON sub.id = ph.subscription_id
WHERE ph.status = 'completed'
GROUP BY s.id, s.service_name, s.category;
