ALTER TABLE employees
ADD COLUMN IF NOT EXISTS verification_status TEXT;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS verification_decided_at TIMESTAMPTZ;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS verification_rejected_reason TEXT;

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS verified_by_telegram_id BIGINT;

UPDATE employees
SET verification_status = CASE
    WHEN is_verified = TRUE THEN 'verified'
    ELSE 'pending'
END
WHERE verification_status IS NULL;

ALTER TABLE employees
ALTER COLUMN verification_status SET DEFAULT 'pending';

ALTER TABLE employees
ALTER COLUMN verification_status SET NOT NULL;

ALTER TABLE employees
DROP CONSTRAINT IF EXISTS employees_verification_status_check;

ALTER TABLE employees
ADD CONSTRAINT employees_verification_status_check
CHECK (verification_status IN ('pending', 'verified', 'rejected'));

CREATE OR REPLACE FUNCTION sync_employee_verification_fields()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_verified := NEW.verification_status = 'verified';

    IF NEW.verification_status = 'pending' THEN
        NEW.verification_decided_at := NULL;
        NEW.verification_rejected_reason := NULL;
        NEW.verified_by_telegram_id := NULL;
    ELSIF NEW.verification_status = 'verified' THEN
        NEW.verification_decided_at := COALESCE(NEW.verification_decided_at, now());
        NEW.verification_rejected_reason := NULL;
    ELSIF NEW.verification_status = 'rejected' THEN
        NEW.verification_decided_at := COALESCE(NEW.verification_decided_at, now());
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_employee_verification_fields ON employees;

CREATE TRIGGER trg_sync_employee_verification_fields
BEFORE INSERT OR UPDATE OF verification_status, verification_decided_at, verification_rejected_reason, verified_by_telegram_id
ON employees
FOR EACH ROW
EXECUTE FUNCTION sync_employee_verification_fields();

UPDATE employees
SET verification_status = verification_status;

CREATE INDEX IF NOT EXISTS idx_employees_verification_status
ON employees(verification_status);
