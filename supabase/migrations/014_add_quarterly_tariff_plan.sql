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
CHECK (period IN ('day', 'week', 'month', 'quarter'));

UPDATE public.tariff_plans
SET
    name = 'КВАРТАЛЬНЫЙ 💎 Оптимальный',
    card_limit = 180,
    price = 11900,
    description = '180 контактов, лимит 15 в день, срок 90 дней',
    is_active = TRUE
WHERE period = 'quarter';

INSERT INTO public.tariff_plans (name, period, card_limit, price, description, is_active)
SELECT 'КВАРТАЛЬНЫЙ 💎 Оптимальный', 'quarter', 180, 11900, '180 контактов, лимит 15 в день, срок 90 дней', TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM public.tariff_plans
    WHERE period = 'quarter'
);
