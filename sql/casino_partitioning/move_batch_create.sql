CREATE OR REPLACE FUNCTION move_batch(tbl text, ts_column text, batch_size int)
RETURNS int AS $$
DECLARE
    moved_count int;
    sql text;
BEGIN
    sql := format($fmt$
        WITH moved AS (
            DELETE FROM %I
            WHERE ctid IN (
                SELECT ctid
                FROM %I
                WHERE %I >= date_trunc('month', CURRENT_TIMESTAMP - '2 months'::interval)
                LIMIT %s
                FOR UPDATE SKIP LOCKED
            )
            RETURNING *
        )
        INSERT INTO %I
        SELECT * FROM moved
        $fmt$, tbl || '_archive', tbl || '_archive', ts_column, batch_size, tbl);

    EXECUTE sql;
    GET DIAGNOSTICS moved_count = ROW_COUNT;

    RETURN moved_count;
END;
$$ LANGUAGE plpgsql;