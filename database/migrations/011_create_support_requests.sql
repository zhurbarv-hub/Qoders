-- Миграция: Создание таблицы support_requests для обращений клиентов
-- Дата: 2024-12-19
-- Описание: Таблица для хранения обращений клиентов, созданных через Telegram бот

-- Создание таблицы support_requests
CREATE TABLE IF NOT EXISTS support_requests (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    contact_phone VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'new',
    resolution_notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    
    -- Проверка допустимых статусов
    CONSTRAINT check_support_request_status CHECK (status IN ('new', 'in_progress', 'resolved', 'closed'))
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS ix_support_requests_client_id ON support_requests(client_id);
CREATE INDEX IF NOT EXISTS ix_support_requests_status ON support_requests(status);
CREATE INDEX IF NOT EXISTS ix_support_requests_status_created ON support_requests(status, created_at);
CREATE INDEX IF NOT EXISTS ix_support_requests_client_created ON support_requests(client_id, created_at);

-- Комментарии к таблице и колонкам
COMMENT ON TABLE support_requests IS 'Обращения клиентов в службу поддержки через Telegram бот';
COMMENT ON COLUMN support_requests.id IS 'Уникальный идентификатор обращения';
COMMENT ON COLUMN support_requests.client_id IS 'ID клиента из таблицы users';
COMMENT ON COLUMN support_requests.subject IS 'Тема обращения';
COMMENT ON COLUMN support_requests.message IS 'Текст обращения';
COMMENT ON COLUMN support_requests.contact_phone IS 'Телефон для обратной связи';
COMMENT ON COLUMN support_requests.status IS 'Статус: new (новое), in_progress (в работе), resolved (решено), closed (закрыто)';
COMMENT ON COLUMN support_requests.resolution_notes IS 'Заметки администратора о решении проблемы';
COMMENT ON COLUMN support_requests.created_at IS 'Дата и время создания обращения';
COMMENT ON COLUMN support_requests.updated_at IS 'Дата и время последнего обновления';
COMMENT ON COLUMN support_requests.resolved_at IS 'Дата и время решения обращения';

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_support_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_support_requests_updated_at
    BEFORE UPDATE ON support_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_support_requests_updated_at();
