### game_play
1. Revoke table privs
```sql
-- as the postgres user
REVOKE INSERT, UPDATE, DELETE ON game_play FROM ats_owner;
```
2. Create empty parent table, partman configs, and _archive table (with the data).
```sh
uv run dba create-partition-table --config game_play.yaml
```
3. Populate parent from _archive and delete from _archive.
```sh
uv run dba populate-partition-table -c game_play.yaml
```
4. Grant table privs
```sql
-- as the postgres user
GRANT INSERT, UPDATE, DELETE ON game_play TO ats_owner;
```