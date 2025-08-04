```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-cert-1mi fbg-cert-1mi-postgresql)
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_play.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_rgs_game_rounds.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_tips.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_w2g_gameplay_non_wv.sql -v ON_ERROR_STOP=1
```

```sh
# ats-database-scripts
poetry run python icasino/game_play_partition.py partition-job --stages cert --targets fbg-cert-1mi
poetry run python icasino/rgs_game_rounds_partition.py partition-job --stages cert --targets fbg-cert-1mi
poetry run python icasino/game_tips_partition.py partition-job --stages cert --targets fbg-cert-1mi
poetry run python icasino/w2g_gameplay_partition.py partition-job --stages cert --targets fbg-cert-1mi
```

