ALTER TABLE employees
ADD COLUMN IF NOT EXISTS activity_signal TEXT;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS activity_signal_updated_at TIMESTAMPTZ;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS activity_signal_prompted_at TIMESTAMPTZ;

ALTER TABLE employees
DROP CONSTRAINT IF EXISTS employees_activity_signal_check;

ALTER TABLE employees
ADD CONSTRAINT employees_activity_signal_check
CHECK (activity_signal IN ('high', 'medium', 'low') OR activity_signal IS NULL);

CREATE INDEX IF NOT EXISTS idx_employees_activity_signal_prompted_at
ON employees(activity_signal_prompted_at);

CREATE INDEX IF NOT EXISTS idx_employees_activity_signal_updated_at
ON employees(activity_signal_updated_at DESC);
