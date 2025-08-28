preflight - revert tables
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-inf-dev-1tn fbg-inf-dev-1tn-postgresql)
echo $PGHOST
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_tips.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_rgs_game_rounds.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_play.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_w2g_gameplay_non_prod.sql -v ON_ERROR_STOP=1
```

1. create move_batch function
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-inf-dev-1tn fbg-inf-dev-1tn-postgresql)
echo $PGHOST

psql -d bet_fanatics -f sql/casino_partitioning/move_batch_create.sql -v ON_ERROR_STOP=1
```

2. game_tips
```sh
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh game_tips created 100000
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/5_indexes.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/6_privs.sql -v ON_ERROR_STOP=1
```

3. rgs_game_rounds
```sh
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh rgs_game_rounds round_date 100000
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/5_indexes.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/6_privs.sql -v ON_ERROR_STOP=1
```

4. game_play
```sh
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh game_play placed_time 100000
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/5_indexes.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/6_privs.sql -v ON_ERROR_STOP=1
```

5. w2g_gameplay
```sh
# TODO handle replication
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh w2g_gameplay settlement_time 100000
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/5_indexes.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/6_privs.sql -v ON_ERROR_STOP=1
# TODO handle replication
```

6. drop move_batch function
```sh
psql -q -d bet_fanatics -f sql/casino_partitioning/move_batch_drop.sql -v ON_ERROR_STOP=1
drop rgs_game_rounds_jdavis?
```