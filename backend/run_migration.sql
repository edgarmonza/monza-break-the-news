-- Add image_url column to threads table
ALTER TABLE threads ADD COLUMN IF NOT EXISTS image_url TEXT;

-- Verify the column was added
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'threads' AND column_name = 'image_url';
