-- Миграция 011: Создание таблицы для расписания автоматических бэкапов
-- Дата: 2025-12-19
-- Описание: Добавление функциональности автоматических резервных копий базы данных

-- Создание таблицы backup_schedules
CREATE TABLE IF NOT EXISTS backup_schedules (
    id SERIAL PRIMARY KEY,
    enabled BOOLEAN DEFAULT TRUE,
    frequency VARCHAR(20) NOT NULL DEFAULT 'daily', -- daily, weekly, monthly
    time_of_day TIME NOT NULL DEFAULT '03:00:00',
    day_of_week INTEGER, -- 0=понедельник, 6=воскресенье (для weekly)
    day_of_month INTEGER, -- 1-31 (для monthly)
    retention_days INTEGER NOT NULL DEFAULT 7, -- сколько дней хранить бэкапы
    last_run_at TIMESTAMP,
    next_run_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT valid_frequency CHECK (frequency IN ('daily', 'weekly', 'monthly')),
    CONSTRAINT valid_day_of_week CHECK (day_of_week IS NULL OR (day_of_week >= 0 AND day_of_week <= 6)),
    CONSTRAINT valid_day_of_month CHECK (day_of_month IS NULL OR (day_of_month >= 1 AND day_of_month <= 31)),
    CONSTRAINT valid_retention CHECK (retention_days > 0)
);

-- Комментарии к столбцам
COMMENT ON TABLE backup_schedules IS 'Расписание автоматических резервных копий базы данных';
COMMENT ON COLUMN backup_schedules.enabled IS 'Включено ли автоматическое создание бэкапов';
COMMENT ON COLUMN backup_schedules.frequency IS 'Частота создания бэкапов: daily (ежедневно), weekly (еженедельно), monthly (ежемесячно)';
COMMENT ON COLUMN backup_schedules.time_of_day IS 'Время суток для создания бэкапа';
COMMENT ON COLUMN backup_schedules.day_of_week IS 'День недели для weekly (0=понедельник, 6=воскресенье)';
COMMENT ON COLUMN backup_schedules.day_of_month IS 'День месяца для monthly (1-31)';
COMMENT ON COLUMN backup_schedules.retention_days IS 'Количество дней хранения старых бэкапов';
COMMENT ON COLUMN backup_schedules.last_run_at IS 'Время последнего выполнения бэкапа';
COMMENT ON COLUMN backup_schedules.next_run_at IS 'Запланированное время следующего бэкапа';

-- Создание индексов
CREATE INDEX idx_backup_schedules_enabled ON backup_schedules(enabled);
CREATE INDEX idx_backup_schedules_next_run ON backup_schedules(next_run_at) WHERE enabled = TRUE;

-- Вставка начальной записи расписания (ежедневно в 3:00, хранение 7 дней)
INSERT INTO backup_schedules (enabled, frequency, time_of_day, retention_days)
VALUES (FALSE, 'daily', '03:00:00', 7)
ON CONFLICT DO NOTHING;

-- Создание таблицы истории выполнения бэкапов
CREATE TABLE IF NOT EXISTS backup_history (
    id SERIAL PRIMARY KEY,
    schedule_id INTEGER REFERENCES backup_schedules(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'running', -- running, success, failed
    filename VARCHAR(255),
    size_bytes BIGINT,
    error_message TEXT,
    CONSTRAINT valid_status CHECK (status IN ('running', 'success', 'failed'))
);

-- Комментарии
COMMENT ON TABLE backup_history IS 'История выполнения автоматических бэкапов';
COMMENT ON COLUMN backup_history.status IS 'Статус выполнения: running (выполняется), success (успешно), failed (ошибка)';

-- Создание индексов для истории
CREATE INDEX idx_backup_history_schedule ON backup_history(schedule_id);
CREATE INDEX idx_backup_history_started ON backup_history(started_at DESC);
CREATE INDEX idx_backup_history_status ON backup_history(status);
