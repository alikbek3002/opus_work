ALTER TABLE employees
ADD COLUMN IF NOT EXISTS contact_opens_count INTEGER NOT NULL DEFAULT 0;

UPDATE employees AS e
SET contact_opens_count = COALESCE(v.open_count, 0)
FROM (
    SELECT employee_id, COUNT(*)::INTEGER AS open_count
    FROM card_views
    GROUP BY employee_id
) AS v
WHERE e.id = v.employee_id;

CREATE OR REPLACE FUNCTION sync_employee_contact_opens_count()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE employees
        SET contact_opens_count = COALESCE(contact_opens_count, 0) + 1
        WHERE id = NEW.employee_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE employees
        SET contact_opens_count = GREATEST(COALESCE(contact_opens_count, 0) - 1, 0)
        WHERE id = OLD.employee_id;
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.employee_id IS DISTINCT FROM OLD.employee_id THEN
            UPDATE employees
            SET contact_opens_count = GREATEST(COALESCE(contact_opens_count, 0) - 1, 0)
            WHERE id = OLD.employee_id;

            UPDATE employees
            SET contact_opens_count = COALESCE(contact_opens_count, 0) + 1
            WHERE id = NEW.employee_id;
        END IF;
        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS trg_sync_employee_contact_opens_count ON card_views;

CREATE TRIGGER trg_sync_employee_contact_opens_count
AFTER INSERT OR DELETE OR UPDATE OF employee_id
ON card_views
FOR EACH ROW
EXECUTE FUNCTION sync_employee_contact_opens_count();

CREATE INDEX IF NOT EXISTS idx_employees_contact_opens_count
ON employees(contact_opens_count DESC);
