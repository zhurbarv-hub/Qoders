-- Добавление суперадмина
INSERT INTO admin_users (email, password_hash, full_name, role, is_active)
VALUES (
    'admin@kkt-master.local',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ux5wk5L7GqKy',
    'Master Admin',
    'superadmin',
    TRUE
) ON CONFLICT (email) DO NOTHING;
