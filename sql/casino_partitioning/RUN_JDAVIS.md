# create move_batch function
```sh
psql -d bet_fanatics -f sql/casino_partitioning/move_batch_create.sql -v ON_ERROR_STOP=1
```

# jdavis
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-inf-dev-1tn fbg-inf-dev-1tn-postgresql)
echo $PGHOST

# jdavis (this was inf-dev-tn game_play) Total moved: 25399946 rows | Job elapsed: 701s
# avg batch time 100k rows in 2s, 0 - 800MB lag
# create index times: 2m 30s
# observed autovacuum keeping up on archive and analyze on partitions
#
# performance comparisons:
    # with indexes was double the batch time - avg time 100k rows in 4s, 0 - 1G lag
    # single insert/select 10 mins, 30GB lag
psql -q -d bet_fanatics -f sql/casino_partitioning/jdavis/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/jdavis/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh jdavis placed_time 100000
psql -q -d bet_fanatics -f sql/casino_partitioning/jdavis/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/jdavis/5_indexes.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/jdavis/6_privs.sql -v ON_ERROR_STOP=1
```

# drop move_batch function
```sh
psql -q -d bet_fanatics -f sql/casino_partitioning/move_batch_drop.sql -v ON_ERROR_STOP=1
drop rgs_game_rounds_jdavis?
```