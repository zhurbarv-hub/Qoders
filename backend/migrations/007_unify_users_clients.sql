-- Migration 007: Unify Users and Clients into single Users table
-- Объединение таблиц users и clients в единую таблицу users
-- Date: 2025-12-12
-- Phase: Database Restructuring

-- ============================================
-- STEP 1: Backup existing data
-- ============================================

-- Create temporary backup tables
CREATE TABLE IF NOT EXISTS _backup_users AS SELECT * FROM users;
CREATE TABLE IF NOT EXISTS _backup_clients AS SELECT * FROM clients;
CREATE TABLE IF NOT EXISTS _backup_contacts AS SELECT * FROM contacts;

-- ============================================
-- STEP 2: Create new unified users table
-- ============================================

-- Drop old users table (backed up above)
DROP TABLE IF EXISTS users;

-- Create new unified users table
CREATE TABLE users (
    -- Primary key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- NULL for clients not yet registered
    
    -- Common fields
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'client' CHECK(role IN ('client', 'manager', 'admin')),
    
    -- Client-specific fields (NULL for managers/admins)
    inn VARCHAR(12) UNIQUE,  -- Only for clients (organizations)
    company_name VARCHAR(255),  -- Organization name for clients
    
    -- Contact information (for all users)
    phone VARCHAR(20),
    address TEXT,
    notes TEXT,
    
    -- Telegram integration (primarily for clients)
    telegram_id VARCHAR(50) UNIQUE,
    telegram_username VARCHAR(100),
    registration_code VARCHAR(20) UNIQUE,
    code_expires_at DATETIME,
    first_name VARCHAR(100),  -- From Telegram
    last_name VARCHAR(100),   -- From Telegram
    
    -- Notification settings (only for clients)
    notification_days TEXT DEFAULT '14,7,3',
    notifications_enabled BOOLEAN DEFAULT 1,
    
    -- Status and metadata
    is_active BOOLEAN NOT NULL DEFAULT 1,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_inn ON users(inn) WHERE inn IS NOT NULL;
CREATE INDEX idx_users_telegram_id ON users(telegram_id) WHERE telegram_id IS NOT NULL;
CREATE UNIQUE INDEX idx_users_registration_code ON users(registration_code) WHERE registration_code IS NOT NULL;
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================
-- STEP 3: Migrate data from old tables
-- ============================================

-- Migrate existing admin/manager users from _backup_users
INSERT INTO users (
    id,
    email,
    password_hash,
    full_name,
    role,
    is_active,
    created_at,
    updated_at
)
SELECT 
    id,
    email,
    password_hash,
    COALESCE(full_name, email) as full_name,  -- Fallback to email if full_name is NULL
    COALESCE(role, 'admin') as role,
    COALESCE(is_active, 1) as is_active,
    created_at,
    updated_at
FROM _backup_users;

-- Get max ID from migrated users to continue sequence for clients
-- SQLite autoincrement will handle this automatically

-- Migrate clients from _backup_clients
-- Create users for each client with role='client'
INSERT INTO users (
    email,
    password_hash,
    full_name,
    role,
    inn,
    company_name,
    phone,
    address,
    notes,
    is_active,
    created_at,
    updated_at
)
SELECT 
    COALESCE(c.email, 'client_' || c.id || '@temp.local') as email,  -- Fallback email if missing
    NULL as password_hash,  -- Clients need to register
    COALESCE(c.contact_person, c.name) as full_name,  -- Use contact_person or company name
    'client' as role,
    c.inn,
    c.name as company_name,
    c.phone,
    c.address,
    c.notes,
    COALESCE(c.is_active, 1) as is_active,
    c.created_at,
    c.updated_at
FROM _backup_clients c;

-- Migrate Telegram data from _backup_contacts to users
-- Match by client_id → user with matching inn
UPDATE users
SET 
    telegram_id = (
        SELECT ct.telegram_id 
        FROM _backup_contacts ct 
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    telegram_username = (
        SELECT ct.telegram_username
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    first_name = (
        SELECT ct.first_name
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    last_name = (
        SELECT ct.last_name
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    registration_code = (
        SELECT ct.registration_code
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    code_expires_at = (
        SELECT ct.code_expires_at
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    notification_days = (
        SELECT COALESCE(ct.notification_days, '14,7,3')
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    notifications_enabled = (
        SELECT COALESCE(ct.notifications_enabled, 1)
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    registered_at = (
        SELECT ct.registered_at
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    last_interaction = (
        SELECT ct.last_interaction
        FROM _backup_contacts ct
        JOIN _backup_clients cl ON ct.client_id = cl.id
        WHERE users.inn = cl.inn
        LIMIT 1
    ),
    -- Override contact fields if present in contacts table
    phone = COALESCE(
        (SELECT ct.phone FROM _backup_contacts ct JOIN _backup_clients cl ON ct.client_id = cl.id WHERE users.inn = cl.inn LIMIT 1),
        users.phone
    ),
    email = COALESCE(
        (SELECT ct.email FROM _backup_contacts ct JOIN _backup_clients cl ON ct.client_id = cl.id WHERE users.inn = cl.inn LIMIT 1),
        users.email
    ),
    full_name = COALESCE(
        (SELECT ct.contact_name FROM _backup_contacts ct JOIN _backup_clients cl ON ct.client_id = cl.id WHERE users.inn = cl.inn AND ct.contact_name IS NOT NULL LIMIT 1),
        users.full_name
    )
WHERE role = 'client' AND inn IS NOT NULL;

-- ============================================
-- STEP 4: Update deadlines table
-- ============================================

-- Add user_id column to deadlines
ALTER TABLE deadlines ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;

-- Populate user_id from client_id
UPDATE deadlines
SET user_id = (
    SELECT u.id 
    FROM users u
    JOIN _backup_clients c ON u.inn = c.inn
    WHERE deadlines.client_id = c.id
    LIMIT 1
)
WHERE client_id IS NOT NULL;

-- Create index on user_id
CREATE INDEX idx_deadlines_user_id ON deadlines(user_id);

-- After verification, we can drop client_id column
-- ALTER TABLE deadlines DROP COLUMN client_id;
-- For now, keep it for safety during transition

-- ============================================
-- STEP 5: Drop old tables
-- ============================================

-- Drop old contacts table (data migrated to users)
DROP TABLE IF EXISTS contacts;

-- Drop old clients table (data migrated to users)
DROP TABLE IF EXISTS clients;

-- ============================================
-- STEP 6: Verification queries
-- ============================================

-- These are just comments for manual verification after migration

-- SELECT COUNT(*) as total_users, role, COUNT(*) as count FROM users GROUP BY role;
-- SELECT COUNT(*) as clients_with_telegram FROM users WHERE role='client' AND telegram_id IS NOT NULL;
-- SELECT COUNT(*) as deadlines_with_user FROM deadlines WHERE user_id IS NOT NULL;

-- ============================================
-- STEP 7: Notes
-- ============================================

-- Post-migration tasks:
-- 1. Update backend/models.py - remove Client and Contact models, enhance User model
-- 2. Update backend/schemas.py - unify schemas
-- 3. Update backend/api/clients.py → backend/api/users.py
-- 4. Update backend/api/contacts.py → merge into users.py
-- 5. Update bot handlers to use users instead of clients/contacts
-- 6. Update web frontend to use /api/users instead of /api/clients
-- 7. Test authentication for both web and Telegram
-- 8. After full verification, can drop backup tables:
--    DROP TABLE _backup_users;
--    DROP TABLE _backup_clients;
--    DROP TABLE _backup_contacts;

-- End of migration
