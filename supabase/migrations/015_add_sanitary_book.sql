-- Добавление поля "Санитарная книжка" (has_sanitary_book)
ALTER TABLE employees ADD COLUMN IF NOT EXISTS has_sanitary_book TEXT;
