SELECT COUNT(1) AS "total_rows" FROM game_play;
SELECT COUNT(1) AS "expected_rows_in_partitions" FROM game_play WHERE placed_time >= date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval);
SELECT COUNT(1) AS "expected_rows_in_archive" FROM game_play WHERE placed_time < date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval);
SELECT MIN(placed_time) AS "min_ts", MAX(placed_time) AS "max_ts" FROM game_play;