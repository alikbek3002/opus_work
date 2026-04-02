-- Добавляем столбец daily_limit для тарифов
ALTER TABLE tariff_plans ADD COLUMN IF NOT EXISTS daily_limit INTEGER;

-- Обновляем лимиты, цены и контакты в соответствии с новыми правилами
UPDATE tariff_plans 
SET price = 490, card_limit = 3, daily_limit = NULL 
WHERE period = 'day';

UPDATE tariff_plans 
SET price = 1900, card_limit = 20, daily_limit = 8 
WHERE period = 'week';

UPDATE tariff_plans 
SET price = 4900, card_limit = 60, daily_limit = 12 
WHERE period = 'month';

UPDATE tariff_plans 
SET price = 11900, card_limit = 180, daily_limit = 15 
WHERE period = 'quarter';
