ALTER TABLE w2g_gameplay ADD CONSTRAINT check_tax_status CHECK (tax_status::text = ANY (ARRAY['DEDUCTED'::varchar, 'REFUNDED'::varchar]::text[]));
-- New on control column
CREATE INDEX IF NOT EXISTS w2g_gameplay_settlement_time_idx ON w2g_gameplay (settlement_time);