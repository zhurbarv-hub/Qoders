-- Миграция 008: Создание справочника ОФД
-- Дата: 2025-12-13

-- Создание таблицы справочника ОФД
CREATE TABLE IF NOT EXISTS ofd_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name VARCHAR(200) NOT NULL UNIQUE,
    inn VARCHAR(12),
    website VARCHAR(255),
    support_phone VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_ofd_providers_active ON ofd_providers(is_active);
CREATE INDEX IF NOT EXISTS idx_ofd_providers_name ON ofd_providers(provider_name);

-- Добавление внешнего ключа в таблицу cash_registers
-- Сначала создаем временную таблицу с новой структурой
CREATE TABLE cash_registers_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    fiscal_drive_number VARCHAR(50) NOT NULL,
    register_name VARCHAR(100) NOT NULL,
    installation_address TEXT,
    ofd_provider_id INTEGER,
    notes TEXT,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ofd_provider_id) REFERENCES ofd_providers(id) ON DELETE SET NULL
);

-- Копируем данные из старой таблицы (без поля ofd_name)
INSERT INTO cash_registers_new (
    id, user_id, serial_number, fiscal_drive_number, register_name, 
    installation_address, notes, is_active, created_at, updated_at
)
SELECT 
    id, user_id, serial_number, fiscal_drive_number, register_name,
    installation_address, notes, is_active, created_at, updated_at
FROM cash_registers;

-- Удаляем старую таблицу
DROP TABLE cash_registers;

-- Переименовываем новую таблицу
ALTER TABLE cash_registers_new RENAME TO cash_registers;

-- Восстанавливаем индексы
CREATE INDEX idx_cash_registers_user ON cash_registers(user_id);
CREATE INDEX idx_cash_registers_serial ON cash_registers(serial_number);
CREATE INDEX idx_cash_registers_active ON cash_registers(is_active);

-- Заполнение справочника ОФД начальными данными (популярные российские ОФД)
INSERT INTO ofd_providers (provider_name, inn, website, support_phone) VALUES
('ОФД.ру', '7704211201', 'https://ofd.ru', '8-800-250-07-22'),
('Такском', '7704358518', 'https://www.taxcom.ru', '8-800-250-05-29'),
('Платформа ОФД', '7709364346', 'https://platformaofd.ru', '8-800-707-61-44'),
('Контур.ОФД', '6663003127', 'https://ofd.kontur.ru', '8-800-100-49-13'),
('Эвотор.ОФД', '9715260691', 'https://evotor.ru/ofd', '8-800-234-00-09'),
('Первый ОФД', '7704549043', 'https://1-ofd.ru', '8-800-775-75-65'),
('СБИС ОФД', '5405293673', 'https://sbis.ru/ofd', '8-800-234-78-67'),
('Яндекс.ОФД', '7736207543', 'https://ofd.yandex.ru', '8-800-234-24-80'),
('Тензор', '5405293673', 'https://tensor.ru', '8-800-333-14-08'),
('Астрал-М', '7728699517', 'https://astralnalog.ru', '8-800-700-15-58');

-- Комментарий о завершении миграции
-- Миграция завершена успешно
