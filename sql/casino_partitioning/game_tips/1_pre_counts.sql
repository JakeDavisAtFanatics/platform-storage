SELECT COUNT(1) AS "total_rows" FROM game_tips;
SELECT COUNT(1) AS "expected_rows_in_partitions" FROM game_tips WHERE created >= date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval);
SELECT COUNT(1) AS "expected_rows_in_archive" FROM game_tips WHERE created < date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval);
SELECT MIN(created) AS "min_ts", MAX(created) AS "max_ts" FROM game_tips;