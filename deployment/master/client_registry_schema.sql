-- ============================================
-- KKT Master Distribution Server
-- Client Registry Database Schema
-- ============================================

-- Drop existing tables if recreating (осторожно!)
DROP TABLE IF EXISTS deployment_history CASCADE;
DROP TABLE IF EXISTS deployed_instances CASCADE;
DROP TABLE IF EXISTS admin_users CASCADE;
DROP TABLE IF EXISTS available_releases CASCADE;

-- ============================================
-- Таблица: Администраторы системы развертывания
-- ============================================
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'deployer', -- superadmin, deployer
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_active ON admin_users(is_active);

-- ============================================
-- Таблица: Развернутые инсталляции
-- ============================================
CREATE TABLE deployed_instances (
    id SERIAL PRIMARY KEY,
    instance_name VARCHAR(100) NOT NULL,
    client_company VARCHAR(255) NOT NULL,
    vds_ip VARCHAR(45) NOT NULL,
    domain VARCHAR(255),
    deployed_version VARCHAR(20) NOT NULL,
    deployed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_health_check TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'active', -- active, inactive, error
    notes TEXT,
    admin_email VARCHAR(255),
    admin_phone VARCHAR(20),
    telegram_bot_token VARCHAR(100),
    telegram_admin_ids TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deployed_instances_status ON deployed_instances(status);
CREATE INDEX idx_deployed_instances_domain ON deployed_instances(domain);
CREATE INDEX idx_deployed_instances_company ON deployed_instances(client_company);

-- ============================================
-- Таблица: История развертываний и обновлений
-- ============================================
CREATE TABLE deployment_history (
    id SERIAL PRIMARY KEY,
    instance_id INTEGER REFERENCES deployed_instances(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- deploy, update, rollback, health_check
    from_version VARCHAR(20),
    to_version VARCHAR(20),
    initiated_by VARCHAR(100), -- admin email or 'auto'
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress', -- in_progress, success, failed
    error_log TEXT,
    notes TEXT
);

CREATE INDEX idx_deployment_history_instance ON deployment_history(instance_id);
CREATE INDEX idx_deployment_history_action ON deployment_history(action);
CREATE INDEX idx_deployment_history_status ON deployment_history(status);
CREATE INDEX idx_deployment_history_started ON deployment_history(started_at);

-- ============================================
-- Таблица: Доступные релизы (из GitHub)
-- ============================================
CREATE TABLE available_releases (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    release_date TIMESTAMP NOT NULL,
    github_url VARCHAR(500) NOT NULL,
    download_url VARCHAR(500) NOT NULL,
    checksum_sha256 VARCHAR(64),
    notes TEXT,
    is_test_release BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_available_releases_version ON available_releases(version);
CREATE INDEX idx_available_releases_date ON available_releases(release_date);

-- ============================================
-- ПРЕДСТАВЛЕНИЯ (VIEWS)
-- ============================================

-- Активные инсталляции с последней проверкой
CREATE VIEW v_active_instances AS
SELECT 
    i.id,
    i.instance_name,
    i.client_company,
    i.domain,
    i.deployed_version,
    i.deployed_at,
    i.last_health_check,
    EXTRACT(EPOCH FROM (NOW() - i.last_health_check))/3600 AS hours_since_health_check,
    i.status,
    i.admin_email
FROM deployed_instances i
WHERE i.status = 'active'
ORDER BY i.deployed_at DESC;

-- Статистика развертываний
CREATE VIEW v_deployment_stats AS
SELECT 
    COUNT(DISTINCT i.id) AS total_instances,
    COUNT(DISTINCT CASE WHEN i.status = 'active' THEN i.id END) AS active_instances,
    COUNT(DISTINCT CASE WHEN i.status = 'inactive' THEN i.id END) AS inactive_instances,
    COUNT(DISTINCT CASE WHEN i.status = 'error' THEN i.id END) AS error_instances,
    COUNT(DISTINCT CASE WHEN h.action = 'deploy' AND h.status = 'success' THEN h.id END) AS successful_deployments,
    COUNT(DISTINCT CASE WHEN h.action = 'deploy' AND h.status = 'failed' THEN h.id END) AS failed_deployments,
    MAX(i.deployed_at) AS last_deployment_date
FROM deployed_instances i
LEFT JOIN deployment_history h ON i.id = h.instance_id;

-- ============================================
-- ФУНКЦИИ
-- ============================================

-- Функция обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для автообновления updated_at
CREATE TRIGGER update_admin_users_updated_at
    BEFORE UPDATE ON admin_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deployed_instances_updated_at
    BEFORE UPDATE ON deployed_instances
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- НАЧАЛЬНЫЕ ДАННЫЕ
-- ============================================

-- Создание суперадмина (пароль: admin123)
-- Хеш bcrypt для пароля "admin123"
INSERT INTO admin_users (email, password_hash, full_name, role, is_active)
VALUES (
    'admin@kkt-master.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ux5wk5L7GqKy',
    'Master Admin',
    'superadmin',
    TRUE
);

-- Комментарии к таблицам
COMMENT ON TABLE admin_users IS 'Администраторы системы развертывания KKT';
COMMENT ON TABLE deployed_instances IS 'Реестр всех развернутых инсталляций KKT';
COMMENT ON TABLE deployment_history IS 'История всех операций развертывания и обновлений';
COMMENT ON TABLE available_releases IS 'Каталог доступных релизов из GitHub';
