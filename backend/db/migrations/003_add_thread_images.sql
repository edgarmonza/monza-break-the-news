-- Migration 003: Add image_url to threads table
-- For storing Unsplash background images

ALTER TABLE threads ADD COLUMN IF NOT EXISTS image_url TEXT;

COMMENT ON COLUMN threads.image_url IS 'Unsplash background image URL for thread hero card';
