SELECT COUNT(1) AS "rows_in_partitions" FROM rgs_game_rounds;
SELECT MIN(round_date) AS "min_ts_in_partitions", MAX(round_date) AS "max_ts_in_partitions" FROM rgs_game_rounds;
SELECT COUNT(1) AS "rows_in_archive" FROM rgs_game_rounds_archive;
SELECT MIN(round_date) AS "min_ts_in_archive", MAX(round_date) AS "max_ts_in_archive" FROM rgs_game_rounds_archive;