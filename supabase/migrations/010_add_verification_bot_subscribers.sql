CREATE TABLE IF NOT EXISTS verification_bot_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id BIGINT NOT NULL UNIQUE,
    chat_type TEXT,
    user_id BIGINT,
    username TEXT,
    full_name TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    subscribed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE verification_bot_subscribers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "verification_bot_subscribers_service_all" ON verification_bot_subscribers;
CREATE POLICY "verification_bot_subscribers_service_all" ON verification_bot_subscribers
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_verification_bot_subscribers_active
ON verification_bot_subscribers(is_active);
