[Confluence Partitioning Verification And Results](https://betfanatics.atlassian.net/wiki/spaces/~712020e46643aef5b74b8caaf2476955d16cef/pages/1836253275/WV+Partitioning+Results+-+cleanup+re-partitioning)

Revert `game_play`, `rgs_game_rounds`, and `game_tips`
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-prod-1wv fbg-prod-1wv-postgresql)
echo $PGHOST
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_tips.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_rgs_game_rounds.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_play.sql -v ON_ERROR_STOP=1
```
By hand, revert `w2g_gameplay` running steps in `sql/wv_casino_fix_partitioning/revert_w2g_gameplay_prod.md`

Once all tables reverted, in `ats-database-scripts`, run partitioning scripts
```sh
# Run in ats-database-scripts
poetry run python icasino/game_tips_partition.py partition-job --stages prod --targets fbg-prod-1wv
poetry run python icasino/rgs_game_rounds_partition.py partition-job --stages prod --targets fbg-prod-1wv
poetry run python icasino/game_play_partition.py partition-job --stages prod --targets fbg-prod-1wv
poetry run python icasino/w2g_gameplay_partition.py partition-job --stages prod --targets fbg-prod-1wv
```

