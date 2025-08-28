DO $$
BEGIN
    RAISE NOTICE 'Starting transaction...';

    RAISE NOTICE 'Creating _archive table...';
    ALTER TABLE public.w2g_gameplay RENAME TO w2g_gameplay_archive;

    RAISE NOTICE 'Dropping contraints from _archive table...';
    ALTER TABLE public.w2g_gameplay_archive DROP CONSTRAINT w2g_gameplay_pkey;
    ALTER TABLE public.w2g_gameplay_archive DROP CONSTRAINT check_tax_status;

    -- None RAISE NOTICE 'Dropping indexes from _archive table...';

    RAISE NOTICE 'Creating parent table...';
    CREATE TABLE public.w2g_gameplay (LIKE public.w2g_gameplay_archive, PRIMARY KEY (id, settlement_time)) PARTITION BY RANGE (settlement_time);

    RAISE NOTICE 'Revoking privs from ats_owner...';
    REVOKE INSERT, UPDATE, DELETE ON w2g_gameplay FROM ats_owner;

    RAISE NOTICE 'Creating partman configs...';
    PERFORM partman.create_parent(
        p_parent_table := 'public.w2g_gameplay',
        p_control := 'settlement_time',
        p_interval := '1 month',
        p_type := 'range',
        p_premake := 3,
        p_start_partition := to_char(date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval), 'YYYY-MM-DD HH24:MI:SS')
    );

    RAISE NOTICE 'Updating partman retention...';
    UPDATE partman.part_config SET retention = '2 months', retention_keep_table = true WHERE parent_table = 'public.w2g_gameplay';

    RAISE NOTICE 'Not granting privs back to ats_owner. Table not populated yet...';

    RAISE NOTICE 'DONE.';
END$$;