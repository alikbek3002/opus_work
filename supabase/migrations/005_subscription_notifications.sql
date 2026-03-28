CREATE TABLE IF NOT EXISTS subscription_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employer_id UUID NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
    subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('expiring_3d', 'expiring_1d', 'expired')),
    sent_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (subscription_id, notification_type)
);

ALTER TABLE subscription_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "subscription_notifications_service_all" ON subscription_notifications
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_subscriptions_expires_at
ON subscriptions(expires_at);

CREATE INDEX IF NOT EXISTS idx_subscription_notifications_subscription_type
ON subscription_notifications(subscription_id, notification_type);
