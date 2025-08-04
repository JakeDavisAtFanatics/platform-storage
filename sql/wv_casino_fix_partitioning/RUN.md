```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-test-1nj fbg-test-1nj-postgresql)
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_play.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_rgs_game_rounds.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_tips.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_w2g_gameplay_non_wv.sql -v ON_ERROR_STOP=1
```