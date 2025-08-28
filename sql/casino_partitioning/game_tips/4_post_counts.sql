SELECT COUNT(1) AS "rows_in_partitions" FROM game_tips;
SELECT MIN(created) AS "min_ts_in_partitions", MAX(created) AS "max_ts_in_partitions" FROM game_tips;
SELECT COUNT(1) AS "rows_in_archive" FROM game_tips_archive;
SELECT MIN(created) AS "min_ts_in_archive", MAX(created) AS "max_ts_in_archive" FROM game_tips_archive;