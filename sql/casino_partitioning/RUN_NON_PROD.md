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

2. game_tips (not tested)
```sh
tail -F sql/casino_partitioning/game_tips/game_tips.log
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh game_tips created 100000
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/5_indexes.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_tips/6_privs.sql -v ON_ERROR_STOP=1
```

3. rgs_game_rounds (not tested)
```sh
tail -F sql/casino_partitioning/rgs_game_rounds/rgs_game_rounds.log
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh rgs_game_rounds round_date 100000
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/5_indexes.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/rgs_game_rounds/6_privs.sql -v ON_ERROR_STOP=1
```

4. game_play
```sh
tail -F sql/casino_partitioning/game_play/game_play.log
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh game_play placed_time 100000 # Fri Aug 29 10:36:02 CDT 2025 -> Batch moved 0 rows in 4s | Total moved: 25399946 rows | Job elapsed: 725s
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/5_indexes.sql -v ON_ERROR_STOP=1 # 2m32s
psql -q -d bet_fanatics -f sql/casino_partitioning/game_play/6_privs.sql -v ON_ERROR_STOP=1
```

5. w2g_gameplay
```sh
# TODO handle replication
tail -F sql/casino_partitioning/w2g_gameplay/w2g_gameplay.log
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/1_pre_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/2_partition.sql -v ON_ERROR_STOP=1
bash sql/casino_partitioning/move_batch.sh w2g_gameplay settlement_time 100000 # Fri Aug 29 10:48:46 CDT 2025 -> Batch moved 0 rows in 1s | Total moved: 1204020 rows | Job elapsed: 27s
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/4_post_counts.sql -v ON_ERROR_STOP=1
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/5_indexes.sql -v ON_ERROR_STOP=1 # 27s
psql -q -d bet_fanatics -f sql/casino_partitioning/w2g_gameplay/6_privs.sql -v ON_ERROR_STOP=1
# TODO handle replication
```

6. drop move_batch function
```sh
psql -q -d bet_fanatics -f sql/casino_partitioning/move_batch_drop.sql -v ON_ERROR_STOP=1
```