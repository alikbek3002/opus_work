DELETE FROM card_views a
USING card_views b
WHERE a.ctid < b.ctid
  AND a.employer_id = b.employer_id
  AND a.employee_id = b.employee_id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_card_views_unique_employer_employee
ON card_views(employer_id, employee_id);

CREATE INDEX IF NOT EXISTS idx_card_views_employer_viewed_at
ON card_views(employer_id, viewed_at DESC);
