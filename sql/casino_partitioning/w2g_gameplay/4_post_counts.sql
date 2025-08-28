SELECT COUNT(1) AS "rows_in_partitions" FROM w2g_gameplay;
SELECT MIN(settlement_time) AS "min_ts_in_partitions", MAX(settlement_time) AS "max_ts_in_partitions" FROM w2g_gameplay;
SELECT COUNT(1) AS "rows_in_archive" FROM w2g_gameplay_archive;
SELECT MIN(settlement_time) AS "min_ts_in_archive", MAX(settlement_time) AS "max_ts_in_archive" FROM w2g_gameplay_archive;