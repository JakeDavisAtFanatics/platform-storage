-- export $(fbg postgres credentials get --skip-refresh --skip-test --env fbg-dev-1nj fbg-dev-1nj-postgresql)
-- psql -d bet_fanatics -f sql/wv_casino_fix_partitioning/revert_w2g_gameplay_wv.sql -v ON_ERROR_STOP=1

-- Check for any rammifications with archive and partitioned data for changing into august

-- All the objects
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

-- Current table
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


-- Current archive table
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


-- Check for copy tables


-- Check for partman configs


# on non prod
Indexes:
    "w2g_gameplay_settlement_time_idx" btree (settlement_time)
Check constraints:
    "w2g_gameplay_tax_status_check" CHECK (tax_status::text = ANY (ARRAY['DEDUCTED'::character varying, 'REFUNDED'::character varying]::text[]))

# on non prod archive
Indexes:
    "w2g_gameplay_archive_pkey" PRIMARY KEY, btree (id)
Check constraints:
    "w2g_gameplay_archive_tax_status_check" CHECK (tax_status::text = ANY (ARRAY['DEDUCTED'::character varying, 'REFUNDED'::character varying]::text[]))

# on prod mi
Indexes:
    "w2g_gameplay_pkey" PRIMARY KEY, btree (id)
Check constraints:
    "check_tax_status" CHECK (tax_status::text = ANY (ARRAY['DEDUCTED'::character varying::text, 'REFUNDED'::character varying::text]))
Publications:
    "pub_fbg_prod_1mi_to_fbg_prod_1"



# cert steps to mirror  (mi and parent)

# mi as postgres user
# undo partman
DELETE FROM partman.part_config where parent_table = 'public.w2g_gameplay';
DROP TABLE partman.w2g_gameplay_template;

# mi as postgres user
# swap out partitioned w2g_gameplay table for regular table
CREATE TABLE w2g_gameplay_fix (LIKE w2g_gameplay_archive INCLUDING ALL);
INSERT INTO w2g_gameplay_fix SELECT * FROM w2g_gameplay;
BEGIN;
ALTER TABLE w2g_gameplay RENAME TO w2g_gameplay_old_partitions;
ALTER TABLE w2g_gameplay_fix RENAME TO w2g_gameplay;
COMMIT;

# mi as postgres user
# rename constraints on regular table to original names for the partition script
ALTER TABLE w2g_gameplay RENAME CONSTRAINT w2g_gameplay_fix_pkey TO w2g_gameplay_pkey;
ALTER TABLE w2g_gameplay RENAME CONSTRAINT w2g_gameplay_archive_tax_status_check TO w2g_gameplay_tax_status_check;

# mi as replication user
ALTER PUBLICATION pub_fbg_cert_1mi_to_fbg_cert_1 ADD TABLE public.w2g_gameplay;

# parent as replication user
ALTER SUBSCRIPTION sub_fbg_cert_1mi_to_fbg_cert_1 REFRESH PUBLICATION;

# THE FOLLOWING STEPS HAVE NOT BEEN COMPLETED YET
# mi as postres user
# cleanup old partitions table
DROP TABLE w2g_gameplay_old_partitions;
# are all the attached partition tables also dropped?
# did the w2g_gameplay_default table get dropped?
# did the sequence get dropped?