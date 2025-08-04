-- export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-dev-1nj fbg-dev-1nj-postgresql)
-- psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_w2g_gameplay_non_wv.sql -v ON_ERROR_STOP=1

-- Drop foreign keys on archive table (outside of trx to avoid errors)
-- None

BEGIN;
-- Backout old partman configs
DELETE FROM partman.part_config WHERE parent_table = 'public.w2g_gameplay';
DROP TABLE partman.w2g_gameplay_template;

-- Create fix table, keeps same sequence, creates indexes, and constraints
CREATE TABLE w2g_gameplay_fix (LIKE w2g_gameplay_archive INCLUDING ALL);

-- Rename primary key on archive table
ALTER TABLE w2g_gameplay_archive RENAME CONSTRAINT w2g_gameplay_archive_pkey TO w2g_gameplay_archive_old_pkey;

-- Drop unique constraints on archive table
ALTER TABLE w2g_gameplay_archive DROP CONSTRAINT w2g_gameplay_archive_tax_status_check;

-- Drop indexes on archive table
-- None

-- Rename archive table
ALTER TABLE w2g_gameplay_archive RENAME TO w2g_gameplay_archive_old;

-- Populate fix table
INSERT INTO w2g_gameplay_fix SELECT * FROM w2g_gameplay;

-- Drop partitioned table, drops all partitions
DROP TABLE w2g_gameplay;

-- Rename fix table
ALTER TABLE w2g_gameplay_fix RENAME TO w2g_gameplay;

-- Rename primary/unique constraints on new table
ALTER TABLE w2g_gameplay RENAME CONSTRAINT w2g_gameplay_fix_pkey TO w2g_gameplay_pkey;
ALTER TABLE w2g_gameplay RENAME CONSTRAINT w2g_gameplay_fix_tax_status_check TO check_tax_status;

-- Rename indexes on new table
-- None

COMMIT;