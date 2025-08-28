SELECT COUNT(1) AS "rows_in_partitions" FROM game_play;
SELECT MIN(placed_time) AS "min_ts_in_partitions", MAX(placed_time) AS "max_ts_in_partitions" FROM game_play;
SELECT COUNT(1) AS "rows_in_archive" FROM game_play_archive;
SELECT MIN(placed_time) AS "min_ts_in_archive", MAX(placed_time) AS "max_ts_in_archive" FROM game_play_archive;