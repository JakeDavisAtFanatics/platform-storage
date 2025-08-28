DO $$
BEGIN
    RAISE NOTICE 'Starting transaction...';

    RAISE NOTICE 'Creating _archive table...';
    ALTER TABLE public.game_play RENAME TO game_play_archive;

    RAISE NOTICE 'Dropping contraints from _archive table...';
    ALTER TABLE public.game_play_archive DROP CONSTRAINT game_play_pkey;
    ALTER TABLE public.game_play_archive DROP CONSTRAINT id_pkey;

    RAISE NOTICE 'Dropping indexes from _archive table...';
    DROP INDEX game_play_acco_id_round_id_idx;
    DROP INDEX game_play_play_id_idx;
    DROP INDEX game_play_round_id_status_idx;

    RAISE NOTICE 'Creating parent table...';
    CREATE TABLE public.game_play (LIKE public.game_play_archive, PRIMARY KEY (id, placed_time)) PARTITION BY RANGE (placed_time);

    RAISE NOTICE 'Revoking privs from ats_owner...';
    REVOKE INSERT, UPDATE, DELETE ON game_play FROM ats_owner;

    RAISE NOTICE 'Creating partman configs...';
    PERFORM partman.create_parent(
        p_parent_table := 'public.game_play',
        p_control := 'placed_time',
        p_interval := '1 month',
        p_type := 'range',
        p_premake := 3,
        p_start_partition := to_char(date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval), 'YYYY-MM-DD HH24:MI:SS')
    );

    RAISE NOTICE 'Updating partman retention...';
    UPDATE partman.part_config SET retention = '2 months', retention_keep_table = true WHERE parent_table = 'public.game_play';

    RAISE NOTICE 'Not granting privs back to ats_owner. Table not populated yet...';

    RAISE NOTICE 'DONE.';
END$$;