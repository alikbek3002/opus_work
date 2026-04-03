-- Обновление тарифов под "OPUS Анкеты" и ранний доступ
-- Лимиты:
-- Пробный: 3 контакта
-- Неделя: 25 контактов, 8 в день
-- Месяц: 65 контактов, 15 в день
-- Квартал: 180 контактов, 22 в день

ALTER TABLE tariff_plans
ADD COLUMN IF NOT EXISTS daily_limit INTEGER;

-- Для некоторых баз эти поля в subscriptions ещё не добавлены
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS daily_limit INTEGER;

ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS daily_views_used INTEGER;

ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS daily_views_remaining INTEGER;

UPDATE tariff_plans
SET
    name = 'Пробный',
    card_limit = 3,
    daily_limit = NULL,
    description = 'Пробный доступ: 3 контакта'
WHERE period = 'day';

UPDATE tariff_plans
SET
    name = 'Неделя',
    card_limit = 25,
    daily_limit = 8,
    description = '25 контактов, до 8 в день (скидка 34%)'
WHERE period = 'week';

UPDATE tariff_plans
SET
    name = 'Месяц',
    card_limit = 65,
    daily_limit = 15,
    description = '65 контактов, до 15 в день (скидка 45%)'
WHERE period = 'month';

UPDATE tariff_plans
SET
    name = 'Квартал',
    card_limit = 180,
    daily_limit = 22,
    description = '180 контактов, до 22 в день (скидка 40%)'
WHERE period = 'quarter';

-- Синхронизация дневных лимитов для уже созданных подписок
UPDATE subscriptions AS s
SET daily_limit = CASE tp.period
    WHEN 'week' THEN 8
    WHEN 'month' THEN 15
    WHEN 'quarter' THEN 22
    ELSE NULL
END
FROM tariff_plans AS tp
WHERE s.tariff_id = tp.id;

UPDATE subscriptions AS s
SET
    daily_views_used = COALESCE(s.daily_views_used, 0),
    daily_views_remaining = CASE
        WHEN s.daily_limit IS NULL THEN NULL
        ELSE LEAST(COALESCE(s.cards_remaining, 0), s.daily_limit)
    END;
