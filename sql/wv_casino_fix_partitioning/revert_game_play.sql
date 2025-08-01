-- export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-dev-1nj fbg-dev-1nj-postgresql)
-- psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_play.sql -v ON_ERROR_STOP=1

BEGIN;

-- Create fix table, keeps same sequence, creates indexes, and constraints
CREATE TABLE game_play_fix (LIKE game_play_archive INCLUDING ALL);

-- Populate archive table to keep for backup
INSERT INTO game_play_archive SELECT * FROM game_play;

-- Drop foreign keys on archive table
ALTER TABLE game_play_archive DROP CONSTRAINT game_play_fund_type_id_fkey;
ALTER TABLE game_play_archive DROP CONSTRAINT game_play_wallet_type_id_fkey;

-- Drop primary/unique constraints on archive table
ALTER TABLE game_play_archive DROP CONSTRAINT game_play_non_partitioned_pkey;
ALTER TABLE game_play_archive DROP CONSTRAINT id_pkey;

-- Drop indexes on archive table
DROP INDEX game_play_non_partitioned_acco_id_round_id_idx;
DROP INDEX game_play_non_partitioned_play_id_idx;
DROP INDEX game_play_non_partitioned_round_id_status_idx;

-- Rename archive table
ALTER TABLE game_play_archive RENAME TO game_play_archive_old;

-- Populate fix table
INSERT INTO game_play_fix SELECT * FROM game_play_archive_old;

-- Drop partitioned table, drops all partitions, safe because all data is in archive
DROP TABLE game_play;

-- Rename fix table
ALTER TABLE game_play_fix RENAME TO game_play;

-- Rename primary/unique constraints on new table
ALTER TABLE game_play RENAME CONSTRAINT game_play_fix_pkey TO game_play_pkey;
ALTER TABLE game_play RENAME CONSTRAINT game_play_fix_id_key TO id_pkey;

-- Rename indexes on new table
ALTER INDEX game_play_fix_acco_id_round_id_idx RENAME TO game_play_acco_id_round_id_idx;
ALTER INDEX game_play_fix_play_id_idx RENAME TO game_play_play_id_idx;
ALTER INDEX game_play_fix_round_id_status_idx RENAME TO game_play_round_id_status_idx;

COMMIT;

-- I did not put back foreign keys since these were not existing on the partitioned tables. This is from PROD MI game_play:
-- Foreign-key constraints:
--    "game_play_fund_type_id_fkey" FOREIGN KEY (fund_type_id) REFERENCES fund_type(id) DEFERRABLE INITIALLY DEFERRED
--    "game_play_wallet_type_id_fkey" FOREIGN KEY (wallet_type_id) REFERENCES wallet_type(id) DEFERRABLE INITIALLY DEFERRED