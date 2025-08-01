-- export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-dev-1nj fbg-dev-1nj-postgresql)
-- psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_rgs_game_rounds.sql -v ON_ERROR_STOP=1

BEGIN;

-- Create fix table, keeps same sequence, creates indexes, and constraints
CREATE TABLE rgs_game_rounds_fix (LIKE rgs_game_rounds_archive INCLUDING ALL);

-- Drop foreign keys on archive table
-- None

-- Drop primary/unique constraints on archive table
ALTER TABLE rgs_game_rounds_archive DROP CONSTRAINT rgs_game_rounds_archive_pkey;
ALTER TABLE rgs_game_rounds_archive DROP CONSTRAINT rgs_game_rounds_archive_ext_round_id_rgs_id_key;

-- Drop indexes on archive table
-- None

-- Rename archive table
ALTER TABLE rgs_game_rounds_archive RENAME TO rgs_game_rounds_archive_old;

-- Populate fix table
INSERT INTO rgs_game_rounds_fix SELECT * FROM rgs_game_rounds;

-- Drop partitioned table, drops all partitions, safe because all data is in archive
DROP TABLE rgs_game_rounds;

-- Rename fix table
ALTER TABLE rgs_game_rounds_fix RENAME TO rgs_game_rounds;

-- Rename primary/unique constraints on new table
ALTER TABLE rgs_game_rounds RENAME CONSTRAINT rgs_game_rounds_fix_pkey TO rgs_game_rounds_pkey;
ALTER TABLE rgs_game_rounds RENAME CONSTRAINT rgs_game_rounds_fix_ext_round_id_rgs_id_key TO rgs_game_rounds_ext_round_id_rgs_id_key;

-- Rename indexes on new table
-- None

COMMIT;