DO $$
BEGIN
    RAISE NOTICE 'Starting transaction...';

    RAISE NOTICE 'Creating _archive table...';
    ALTER TABLE public.game_tips RENAME TO game_tips_archive;

    -- None RAISE NOTICE 'Dropping contraints from _archive table...';

    RAISE NOTICE 'Dropping indexes from _archive table...';
    DROP INDEX game_tips_transaction_idx;

    RAISE NOTICE 'Creating parent table...';
    CREATE TABLE public.game_tips (LIKE public.game_tips_archive, PRIMARY KEY (id, created)) PARTITION BY RANGE (created);

    RAISE NOTICE 'Revoking privs from ats_owner...';
    REVOKE INSERT, UPDATE, DELETE ON game_tips FROM ats_owner;

    RAISE NOTICE 'Creating partman configs...';
    PERFORM partman.create_parent(
        p_parent_table := 'public.game_tips',
        p_control := 'created',
        p_interval := '1 month',
        p_type := 'range',
        p_premake := 3,
        p_start_partition := to_char(date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval), 'YYYY-MM-DD HH24:MI:SS')
    );

    RAISE NOTICE 'Updating partman retention...';
    UPDATE partman.part_config SET retention = '2 months', retention_keep_table = true WHERE parent_table = 'public.game_tips';

    RAISE NOTICE 'Not granting privs back to ats_owner. Table not populated yet...';

    RAISE NOTICE 'DONE.';
END$$;