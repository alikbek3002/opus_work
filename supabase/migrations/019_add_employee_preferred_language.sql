ALTER TABLE employees
ADD COLUMN IF NOT EXISTS preferred_language TEXT DEFAULT 'ru';
