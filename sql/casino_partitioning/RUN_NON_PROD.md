1. Revert `game_play`, `rgs_game_rounds`, `game_tips`, and `w2g_gameplay`
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-inf-dev-1nj fbg-inf-dev-1nj-postgresql)
echo $PGHOST
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_tips.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_rgs_game_rounds.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_game_play.sql -v ON_ERROR_STOP=1
psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_w2g_gameplay_non_prod.sql -v ON_ERROR_STOP=1
```

2. `game_tips`

- Revoke table privs
```sql
-- as the postgres user
SELECT COUNT(1) FROM game_tips; SELECT COUNT(1) FROM game_tips_archive_old;
REVOKE INSERT, UPDATE, DELETE ON game_tips FROM ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'game_tips';
```
- Create empty parent table, partman configs, and _archive table (with the data).
```sh
uv run dba create-partition-table --config sql/casino_partitioning/game_tips.yaml
```
- Populate parent from _archive and delete from _archive.
```sh
uv run dba populate-partition-table -c sql/casino_partitioning/game_tips.yaml
```
- Grant table privs
```sql
-- as the postgres user
GRANT INSERT, UPDATE, DELETE ON game_tips TO ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'game_tips';
SELECT COUNT(1) FROM game_tips; SELECT COUNT(1) FROM game_tips_archive;
```

3. `rgs_game_rounds`

- Revoke table privs
```sql
-- as the postgres user
SELECT COUNT(1) FROM rgs_game_rounds; SELECT COUNT(1) FROM rgs_game_rounds_archive_old;
REVOKE INSERT, UPDATE, DELETE ON rgs_game_rounds FROM ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'rgs_game_rounds';
```
- Create empty parent table, partman configs, and _archive table (with the data).
```sh
uv run dba create-partition-table --config sql/casino_partitioning/rgs_game_rounds.yaml
```
- Populate parent from _archive and delete from _archive.
```sh
uv run dba populate-partition-table -c sql/casino_partitioning/rgs_game_rounds.yaml
```
- Grant table privs
```sql
-- as the postgres user
GRANT INSERT, UPDATE, DELETE ON rgs_game_rounds TO ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'rgs_game_rounds';
SELECT COUNT(1) FROM rgs_game_rounds; SELECT COUNT(1) FROM rgs_game_rounds_archive;
```

4. `game_play`

- Revoke table privs
```sql
-- as the postgres user
SELECT COUNT(1) FROM game_play; SELECT COUNT(1) FROM game_play_archive_old;
REVOKE INSERT, UPDATE, DELETE ON game_play FROM ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'game_play';
```
- Create empty parent table, partman configs, and _archive table (with the data).
```sh
uv run dba create-partition-table --config sql/casino_partitioning/game_play.yaml
```
- Populate parent from _archive and delete from _archive.
```sh
uv run dba populate-partition-table -c sql/casino_partitioning/game_play.yaml
```
- Grant table privs
```sql
-- as the postgres user
GRANT INSERT, UPDATE, DELETE ON game_play TO ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'game_play';
SELECT COUNT(1) FROM game_play; SELECT COUNT(1) FROM game_play_archive;
```

5. `w2g_gameplay`

- Revoke table privs
```sql
-- as the postgres user
SELECT COUNT(1) FROM w2g_gameplay; SELECT COUNT(1) FROM w2g_gameplay_archive_old;
REVOKE INSERT, UPDATE, DELETE ON w2g_gameplay FROM ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'w2g_gameplay';
```
- Create empty parent table, partman configs, and _archive table (with the data).
```sh
uv run dba create-partition-table --config sql/casino_partitioning/w2g_gameplay.yaml
```
- Populate parent from _archive and delete from _archive.
```sh
uv run dba populate-partition-table -c sql/casino_partitioning/w2g_gameplay.yaml
```
- Grant table privs
```sql
-- as the postgres user
GRANT INSERT, UPDATE, DELETE ON w2g_gameplay TO ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'w2g_gameplay';
SELECT COUNT(1) FROM w2g_gameplay; SELECT COUNT(1) FROM w2g_gameplay_archive;
```