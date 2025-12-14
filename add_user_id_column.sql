-- Add user_id column to deadlines table
ALTER TABLE deadlines ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;

-- Create index
CREATE INDEX IF NOT EXISTS idx_deadlines_user_id ON deadlines(user_id);

-- Copy existing client_id values to user_id (since client_id already references users table)
UPDATE deadlines SET user_id = client_id WHERE user_id IS NULL;

-- Show result
\d deadlines
