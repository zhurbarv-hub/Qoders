-- Migration 006: Add contact management fields
-- Добавление полей для управления контактами клиентов
-- Date: 2025-12-12

-- Добавляем поля для персональных настроек уведомлений
ALTER TABLE contacts ADD COLUMN contact_name TEXT;
ALTER TABLE contacts ADD COLUMN phone TEXT;
ALTER TABLE contacts ADD COLUMN email TEXT;
ALTER TABLE contacts ADD COLUMN notification_days TEXT DEFAULT '14,7,3';
ALTER TABLE contacts ADD COLUMN registration_code TEXT;  -- Убрали UNIQUE, добавим индекс
ALTER TABLE contacts ADD COLUMN code_expires_at DATETIME;
ALTER TABLE contacts ADD COLUMN notes TEXT;

-- Создаём уникальный индекс для registration_code
CREATE UNIQUE INDEX IF NOT EXISTS ix_contacts_registration_code ON contacts(registration_code) WHERE registration_code IS NOT NULL;

-- Обновляем существующие записи - устанавливаем дефолтные дни уведомлений
UPDATE contacts SET notification_days = '14,7,3' WHERE notification_days IS NULL;

-- Комментарии к новым полям:
-- contact_name: ФИО контактного лица
-- phone: Телефон контакта
-- email: Email контакта
-- notification_days: Персональные дни уведомлений (через запятую), например "30,14,7,3"
-- registration_code: Одноразовый код для регистрации через Telegram бот
-- code_expires_at: Срок действия кода регистрации (24 часа)
-- notes: Дополнительные примечания о контакте
