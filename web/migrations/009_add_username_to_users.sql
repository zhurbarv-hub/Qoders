-- Migration: 009_add_username_to_users
-- Description: Добавить поле username (логин) в таблицу users для унификации аутентификации

BEGIN;

-- 1. Добавить колонку username
ALTER TABLE users ADD COLUMN username VARCHAR(50);

-- 2. Создать уникальный индекс (после заполнения данных)
-- CREATE UNIQUE INDEX idx_users_username ON users(username);

-- 3. Временно заполним username значениями из email (до "@")
UPDATE users SET username = SPLIT_PART(email, '@', 1);

-- 4. Теперь можем создать уникальный индекс
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- 5. Сделать поле NOT NULL после заполнения данных
ALTER TABLE users ALTER COLUMN username SET NOT NULL;

COMMIT;
