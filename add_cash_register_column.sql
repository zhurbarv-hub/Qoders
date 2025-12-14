-- Add cash_register_id column to deadlines table
ALTER TABLE deadlines ADD COLUMN IF NOT EXISTS cash_register_id INTEGER;

-- Create index
CREATE INDEX IF NOT EXISTS idx_deadlines_cash_register_id ON deadlines(cash_register_id);

-- Show result
SELECT 'Column added successfully' as status;
