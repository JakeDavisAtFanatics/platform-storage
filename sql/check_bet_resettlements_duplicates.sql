-- for h in $(pg-hosts fbg-dev | grep -v replica | awk '{ print $1}') ; do echo $h ; psql -h $h -U postgres -f check_bet_resettlements_duplicates.sql bet_fanatics > $h.txt 2>&1 ; done

DO $$
DECLARE
    s RECORD;
    query text;
    duplicate_count integer;
BEGIN
    FOR s IN
        SELECT table_schema
        FROM information_schema.tables
        WHERE table_name = 'bet_resettlements'
    LOOP
        query := format(
            'SELECT COUNT(*) FROM (
                SELECT bet_id, settlement_version
                FROM %I.bet_resettlements
                GROUP BY bet_id, settlement_version
                HAVING COUNT(*) > 1
            ) AS duplicates', s.table_schema
        );
        
        EXECUTE query INTO STRICT duplicate_count;
        
        IF duplicate_count > 0 THEN
            RAISE NOTICE 'Found % duplicate(s) in %.bet_resettlements', duplicate_count, s.table_schema;
        ELSE
            RAISE NOTICE 'No duplicates found in %.bet_resettlements', s.table_schema;
        END IF;
    END LOOP;
END $$;
