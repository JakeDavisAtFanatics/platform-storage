SELECT COUNT(1) AS "total_rows" FROM w2g_gameplay;
SELECT COUNT(1) AS "expected_rows_in_partitions" FROM w2g_gameplay WHERE settlement_time >= date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval);
SELECT COUNT(1) AS "expected_rows_in_archive" FROM w2g_gameplay WHERE settlement_time < date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval);
SELECT MIN(settlement_time) AS "min_ts", MAX(settlement_time) AS "max_ts" FROM w2g_gameplay;