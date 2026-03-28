-- ============================================
-- OpusTGBot — Supabase Database Schema
-- ============================================

-- 1. Сотрудники (регистрация через Telegram бот)
CREATE TABLE IF NOT EXISTS employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    gender TEXT,
    telegram_username TEXT,
    phone_number TEXT,
    has_whatsapp BOOLEAN NOT NULL DEFAULT FALSE,
    age INTEGER,
    district TEXT,
    specializations TEXT,
    experience TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    opus_experience TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Работодатели (регистрация через веб-приложение)
CREATE TABLE IF NOT EXISTS employers (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    company_name TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Тарифные планы
CREATE TABLE IF NOT EXISTS tariff_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,               -- «Базовый», «Стандарт», «Премиум»
    period TEXT NOT NULL CHECK (period IN ('week', 'month')),
    card_limit INTEGER NOT NULL,       -- Лимит просмотров карточек
    price INTEGER NOT NULL,            -- Цена в сомах
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Подписки работодателей
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
    tariff_id UUID NOT NULL REFERENCES tariff_plans(id),
    cards_remaining INTEGER NOT NULL,
    starts_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4.1 Напоминания по подпискам
CREATE TABLE IF NOT EXISTS subscription_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('expiring_3d', 'expiring_1d', 'expired')),
    sent_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (subscription_id, notification_type)
);

-- 5. Просмотры карточек (трекинг)
CREATE TABLE IF NOT EXISTS card_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    viewed_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Платежи (Fenik Pay)
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
    tariff_id UUID NOT NULL REFERENCES tariff_plans(id),
    amount INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed')),
    fenik_payment_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- Row Level Security (RLS)
-- ============================================

ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE employers ENABLE ROW LEVEL SECURITY;
ALTER TABLE tariff_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE card_views ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;

-- employees: аутентифицированные пользователи могут читать
CREATE POLICY "employees_select" ON employees
    FOR SELECT TO authenticated
    USING (true);

-- employees: сервисная роль может всё (для бота)
CREATE POLICY "employees_service_all" ON employees
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

-- employers: каждый видит/редактирует только свою запись
CREATE POLICY "employers_select_own" ON employers
    FOR SELECT TO authenticated
    USING (auth.uid() = id);

CREATE POLICY "employers_insert_own" ON employers
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = id);

CREATE POLICY "employers_update_own" ON employers
    FOR UPDATE TO authenticated
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- tariff_plans: все аутентифицированные читают
CREATE POLICY "tariffs_select" ON tariff_plans
    FOR SELECT TO authenticated
    USING (is_active = true);

-- subscriptions: работодатель видит только свои
CREATE POLICY "subscriptions_select_own" ON subscriptions
    FOR SELECT TO authenticated
    USING (employer_id = auth.uid());

-- subscription_notifications: сервисная роль управляет напоминаниями
CREATE POLICY "subscription_notifications_service_all" ON subscription_notifications
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

-- card_views: работодатель видит свои просмотры
CREATE POLICY "card_views_select_own" ON card_views
    FOR SELECT TO authenticated
    USING (employer_id = auth.uid());

-- payments: работодатель видит свои платежи
CREATE POLICY "payments_select_own" ON payments
    FOR SELECT TO authenticated
    USING (employer_id = auth.uid());

-- ============================================
-- Дефолтные тарифные планы
-- ============================================

INSERT INTO tariff_plans (name, period, card_limit, price, description) VALUES
    ('Базовый', 'week', 30, 500, 'Доступ к 30 карточкам сотрудников на неделю'),
    ('Базовый', 'month', 30, 1500, 'Доступ к 30 карточкам сотрудников на месяц'),
    ('Стандарт', 'week', 80, 1000, 'Доступ к 80 карточкам сотрудников на неделю'),
    ('Стандарт', 'month', 80, 3500, 'Доступ к 80 карточкам сотрудников на месяц'),
    ('Премиум', 'week', 200, 2000, 'Доступ к 200 карточкам сотрудников на неделю'),
    ('Премиум', 'month', 200, 7000, 'Доступ к 200 карточкам сотрудников на месяц');

-- ============================================
-- Индексы для производительности
-- ============================================

CREATE INDEX IF NOT EXISTS idx_employees_telegram_id ON employees(telegram_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_employer ON subscriptions(employer_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON subscriptions(employer_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_subscriptions_expires_at ON subscriptions(expires_at);
CREATE INDEX IF NOT EXISTS idx_subscription_notifications_subscription_type ON subscription_notifications(subscription_id, notification_type);
CREATE INDEX IF NOT EXISTS idx_card_views_employer ON card_views(employer_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_card_views_unique_employer_employee ON card_views(employer_id, employee_id);
CREATE INDEX IF NOT EXISTS idx_card_views_employer_viewed_at ON card_views(employer_id, viewed_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_employer ON payments(employer_id);
