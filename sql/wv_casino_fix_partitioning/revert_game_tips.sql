-- export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-dev-1nj fbg-dev-1nj-postgresql)
-- psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_tips.sql -v ON_ERROR_STOP=1

BEGIN;

-- Create fix table, keeps same sequence, creates indexes, and constraints
CREATE TABLE game_tips_fix (LIKE game_tips_archive INCLUDING ALL);

-- Populate archive table to keep for backup
INSERT INTO game_tips_archive SELECT * FROM game_tips;

-- Drop foreign keys on archive table
-- None

-- Drop primary/unique constraints on archive table
-- None

-- Drop indexes on archive table
DROP INDEX game_tips_archive_ext_transaction_id_idx;

-- Rename archive table
ALTER TABLE game_tips_archive RENAME TO game_tips_archive_old;

-- Populate fix table
INSERT INTO game_tips_fix SELECT * FROM game_tips_archive_old;

-- Drop partitioned table, drops all partitions, safe because all data is in archive
DROP TABLE game_tips;

-- Rename fix table
ALTER TABLE game_tips_fix RENAME TO game_tips;

-- Rename primary/unique constraints on new table
-- None

-- Rename indexes on new table
ALTER INDEX game_tips_fix_ext_transaction_id_idx RENAME TO game_tips_transaction_idx;

COMMIT;