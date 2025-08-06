As replication user, drop table from the publication
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-prod-1wv fbg-prod-1wv-postgresql)
```
```sql
ALTER PUBLICATION pub_fbg_prod_1wv_to_fbg_prod_1 DROP TABLE public.w2g_gameplay;
```

As replication user, refresh the subscription
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-prod-1 fbg-prod-1-postgresql)
```
```sql
ALTER SUBSCRIPTION sub_fbg_prod_1wv_to_fbg_prod_1 REFRESH PUBLICATION;
```

As the posstgres user, run the revert steps
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-prod-1wv fbg-prod-1wv-postgresql)
```
```sql
-- Drop foreign keys on archive table (outside of trx to avoid errors)
-- None

BEGIN;
-- Drop the old and unused partitioned table, drops all partitions
DROP TABLE w2g_gameplay_parted;

-- Backout old partman configs
DELETE FROM partman.part_config WHERE parent_table = 'public.w2g_gameplay';
DROP TABLE partman.w2g_gameplay_template;

-- Create fix table, keeps same sequence, creates indexes, and constraints
CREATE TABLE w2g_gameplay_fix (LIKE w2g_gameplay_archive INCLUDING ALL);

-- Rename primary key on archive table
ALTER TABLE w2g_gameplay_archive RENAME CONSTRAINT w2g_gameplay_archive_pkey TO w2g_gameplay_archive_old_pkey;

-- Drop unique constraints on archive table
ALTER TABLE w2g_gameplay_archive DROP CONSTRAINT w2g_gameplay_archive_tax_status_check;

-- Drop indexes on archive table
-- None

-- Rename archive table
ALTER TABLE w2g_gameplay_archive RENAME TO w2g_gameplay_archive_old;

-- Populate fix table
INSERT INTO w2g_gameplay_fix SELECT * FROM w2g_gameplay;

-- Drop old table (owned by replication user incorrectly)
DROP TABLE w2g_gameplay;

-- Rename fix table
ALTER TABLE w2g_gameplay_fix RENAME TO w2g_gameplay;

-- Rename primary/unique constraints on new table
ALTER TABLE w2g_gameplay RENAME CONSTRAINT w2g_gameplay_fix_pkey TO w2g_gameplay_pkey;
ALTER TABLE w2g_gameplay RENAME CONSTRAINT w2g_gameplay_archive_tax_status_check TO check_tax_status;

-- Rename indexes on new table
-- None

-- Check table owner is postgres after creating fix table from archive
-- There was a sequence created by the partitioning script? it doesn't exist on the other envs so should be gone

COMMIT;
```

NOW RUN THE PARTITIONING SCRIPTS IN ATS-DATABASE-SCRIPTS THEN COME BACK HERE WHEN DONE TO SET UP REPLICATION AGAIN.

As replication user, add table to publication
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-prod-1wv fbg-prod-1wv-postgresql)
```
```sql
ALTER PUBLICATION pub_fbg_prod_1wv_to_fbg_prod_1 ADD TABLE public.w2g_gameplay;
```

As replication user, refresh the subscription (DO NOT COPY DATA!)
```sh
export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-prod-1 fbg-prod-1-postgresql)
```
```sql
ALTER SUBSCRIPTION sub_fbg_prod_1wv_to_fbg_prod_1 REFRESH PUBLICATION WITH (copy_data = false);
```

References:
```sql
-- BEFORE: All the objects
 public       | w2g_gameplay                            | table             | replication
 public       | w2g_gameplay_archive                    | table             | postgres
 public       | w2g_gameplay_default                    | table             | postgres
 public       | w2g_gameplay_id_seq                     | sequence          | postgres
 public       | w2g_gameplay_p20250501                  | table             | postgres
 public       | w2g_gameplay_p20250601                  | table             | postgres
 public       | w2g_gameplay_p20250701                  | table             | postgres
 public       | w2g_gameplay_p20250801                  | table             | postgres
 public       | w2g_gameplay_p20250901                  | table             | postgres
 public       | w2g_gameplay_p20251001                  | table             | postgres
 public       | w2g_gameplay_p20251101                  | table             | postgres
 public       | w2g_gameplay_parted                     | partitioned table | postgres

-- BEFORE: Current table
fbg-prod-1wv-postgresql postgres@bet_fanatics=> \d w2g_gameplay
                          Table "public.w2g_gameplay"
       Column       |           Type           | Collation | Nullable | Default 
--------------------+--------------------------+-----------+----------+---------
 id                 | bigint                   |           | not null | 
 game_play_id       | bigint                   |           |          | 
 result_type        | character varying(5)     |           |          | 
 total_payout       | numeric(14,4)            |           |          | 
 total_stake        | numeric(14,4)            |           |          | 
 total_winnings     | numeric(14,4)            |           |          | 
 settlement_time    | timestamp with time zone |           |          | 
 tax_federal        | numeric(14,4)            |           |          | 
 tax_state          | numeric(14,4)            |           |          | 
 tax_on_returns_amt | numeric(14,4)            |           |          | 
 tax_status         | character varying(10)    |           |          | 
 jurisdiction_code  | character varying        |           |          | 
Indexes:
    "w2g_gameplay_copy_pkey" PRIMARY KEY, btree (id)
Check constraints:
    "w2g_gameplay_tax_status_check" CHECK (tax_status::text = ANY (ARRAY['DEDUCTED'::character varying, 'REFUNDED'::character varying]::text[]))
Publications:
    "pub_fbg_prod_1wv_to_fbg_prod_1"


-- BEFORE: Current archive table
fbg-prod-1wv-postgresql postgres@bet_fanatics=> \d w2g_gameplay_archive
                                 Table "public.w2g_gameplay_archive"
       Column       |           Type           | Collation | Nullable |            Default            
--------------------+--------------------------+-----------+----------+-------------------------------
 id                 | bigint                   |           | not null | 
 game_play_id       | bigint                   |           |          | 
 result_type        | character varying(5)     |           |          | 'TYPE1'::character varying
 total_payout       | numeric(14,4)            |           | not null | 
 total_stake        | numeric(14,4)            |           | not null | 
 total_winnings     | numeric(14,4)            |           | not null | 
 settlement_time    | timestamp with time zone |           | not null | now()
 tax_federal        | numeric(14,4)            |           |          | 
 tax_state          | numeric(14,4)            |           |          | 
 tax_on_returns_amt | numeric(14,4)            |           |          | 
 tax_status         | character varying(10)    |           |          | 'DEDUCTED'::character varying
 jurisdiction_code  | character varying        |           |          | 
Indexes:
    "w2g_gameplay_archive_pkey" PRIMARY KEY, btree (id)
Check constraints:
    "w2g_gameplay_archive_tax_status_check" CHECK (tax_status::text = ANY (ARRAY['DEDUCTED'::character varying, 'REFUNDED'::character varying]::text[]))

-- Current target table prod mi
fbg-prod-1mi-postgresql postgres@bet_fanatics=> \d w2g_gameplay
                                     Table "public.w2g_gameplay"
       Column       |           Type           | Collation | Nullable |            Default            
--------------------+--------------------------+-----------+----------+-------------------------------
 id                 | bigint                   |           | not null | 
 game_play_id       | bigint                   |           |          | 
 result_type        | character varying(5)     |           |          | 'TYPE1'::character varying
 total_payout       | numeric(14,4)            |           | not null | 
 total_stake        | numeric(14,4)            |           | not null | 
 total_winnings     | numeric(14,4)            |           | not null | 
 settlement_time    | timestamp with time zone |           | not null | now()
 tax_federal        | numeric(14,4)            |           |          | 
 tax_state          | numeric(14,4)            |           |          | 
 tax_on_returns_amt | numeric(14,4)            |           |          | 
 tax_status         | character varying(10)    |           |          | 'DEDUCTED'::character varying
 jurisdiction_code  | character varying        |           |          | 
Indexes:
    "w2g_gameplay_pkey" PRIMARY KEY, btree (id)
Check constraints:
    "check_tax_status" CHECK (tax_status::text = ANY (ARRAY['DEDUCTED'::character varying::text, 'REFUNDED'::character varying::text]))
Publications:
    "pub_fbg_prod_1mi_to_fbg_prod_1"
```