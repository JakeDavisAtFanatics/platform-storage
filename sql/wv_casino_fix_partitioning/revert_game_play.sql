-- export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-dev-1nj fbg-dev-1nj-postgresql)
-- psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_play.sql -v ON_ERROR_STOP=1

-- Drop foreign keys on archive table (outside of trx to avoid errors)
ALTER TABLE game_play_archive DROP CONSTRAINT game_play_fund_type_id_fkey;
ALTER TABLE game_play_archive DROP CONSTRAINT game_play_wallet_type_id_fkey;

BEGIN;
-- Backout old partman configs
DELETE FROM partman.part_config WHERE parent_table = 'public.game_play';
DROP TABLE partman.game_play_template;

-- Create fix table, keeps same sequence, creates indexes, and constraints
CREATE TABLE game_play_fix (LIKE game_play_archive INCLUDING ALL);

-- Rename primary key on archive table
ALTER TABLE game_play_archive RENAME CONSTRAINT game_play_non_partitioned_pkey TO game_play_archive_old_pkey;

-- Drop unique constraints on archive table
ALTER TABLE game_play_archive DROP CONSTRAINT id_pkey;

-- Drop indexes on archive table
DROP INDEX game_play_non_partitioned_acco_id_round_id_idx;
DROP INDEX game_play_non_partitioned_play_id_idx;
DROP INDEX game_play_non_partitioned_round_id_status_idx;

-- Rename archive table
ALTER TABLE game_play_archive RENAME TO game_play_archive_old;

-- Populate fix table
INSERT INTO game_play_fix SELECT * FROM game_play;

-- Drop partitioned table, drops all partitions
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