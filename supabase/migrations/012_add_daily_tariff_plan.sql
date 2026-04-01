DO $$
DECLARE
    constraint_name text;
BEGIN
    FOR constraint_name IN
        SELECT con.conname
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
        WHERE nsp.nspname = 'public'
          AND rel.relname = 'tariff_plans'
          AND con.contype = 'c'
          AND pg_get_constraintdef(con.oid) ILIKE '%period%'
    LOOP
        EXECUTE format(
            'ALTER TABLE public.tariff_plans DROP CONSTRAINT IF EXISTS %I',
            constraint_name
        );
    END LOOP;
END $$;

ALTER TABLE public.tariff_plans
ADD CONSTRAINT tariff_plans_period_check
CHECK (period IN ('day', 'week', 'month'));

UPDATE public.tariff_plans
SET
    name = '1 день',
    card_limit = 3,
    price = 490,
    description = '3 контакта на 1 день',
    is_active = TRUE
WHERE period = 'day';

INSERT INTO public.tariff_plans (name, period, card_limit, price, description, is_active)
SELECT '1 день', 'day', 3, 490, '3 контакта на 1 день', TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM public.tariff_plans
    WHERE period = 'day'
);
