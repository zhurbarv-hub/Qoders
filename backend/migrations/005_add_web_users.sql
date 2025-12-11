-- Создание таблицы пользователей веб-интерфейса
CREATE TABLE IF NOT EXISTS web_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    telegram_id VARCHAR(50) UNIQUE,
    last_login DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для быстрого поиска
CREATE INDEX idx_web_users_username ON web_users(username);
CREATE INDEX idx_web_users_email ON web_users(email);
CREATE INDEX idx_web_users_role ON web_users(role);
CREATE INDEX idx_web_users_active ON web_users(is_active);

-- Создание тестового администратора
-- Логин: admin
-- Пароль: admin123 (ОБЯЗАТЕЛЬНО СМЕНИТЬ!)
INSERT INTO web_users (username, email, password_hash, full_name, role, is_active)
VALUES (
    'admin',
    'admin@kkt-system.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYdNX.Jxnae',
    'Администратор',
    'admin',
    1
);