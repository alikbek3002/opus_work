-- Оставляем только два активных тарифа:
-- 1) Неделя: 25 контактов, 1900 сом
-- 2) Месяц: 80 контактов, 4900 сом

UPDATE tariff_plans
SET is_active = FALSE;

INSERT INTO tariff_plans (name, period, card_limit, price, description, is_active)
VALUES
    ('Неделя', 'week', 25, 1900, '25 контактов, до 15 в день', TRUE),
    ('Месяц', 'month', 80, 4900, '80 контактов, до 20 в день', TRUE);
