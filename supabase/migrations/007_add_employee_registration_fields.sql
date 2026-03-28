ALTER TABLE employees
ADD COLUMN IF NOT EXISTS photo_file_id TEXT;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS employment_type TEXT;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS ready_for_weekends BOOLEAN;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS about_me TEXT;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS has_recommendations BOOLEAN;
