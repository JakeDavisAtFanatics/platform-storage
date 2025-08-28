SELECT COUNT(1) AS "total_rows" FROM rgs_game_rounds;
SELECT COUNT(1) AS "expected_rows_in_partitions" FROM rgs_game_rounds WHERE round_date >= date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval);
SELECT COUNT(1) AS "expected_rows_in_archive" FROM rgs_game_rounds WHERE round_date < date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval);
SELECT MIN(round_date) AS "min_ts", MAX(round_date) AS "max_ts" FROM rgs_game_rounds;