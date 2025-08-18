from psycopg.sql import SQL, Composed, Literal

from dba.common.sql import Query
from dba.models import PostgresTable


def select_publications_query(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
    pubname AS name,
    NULL AS column,
    NULL AS column
FROM pg_catalog.pg_publication p
     JOIN pg_catalog.pg_publication_namespace pn ON p.oid = pn.pnpubid
     JOIN pg_catalog.pg_class pc ON pc.relnamespace = pn.pnnspid
WHERE pc.oid = {} and pg_catalog.pg_relation_is_publishable({})
UNION
SELECT pubname
     , pg_get_expr(pr.prqual, c.oid)
     , (CASE WHEN pr.prattrs IS NOT NULL THEN
         (SELECT string_agg(attname, ', ')
           FROM pg_catalog.generate_series(0, pg_catalog.array_upper(pr.prattrs::pg_catalog.int2[], 1)) s,
                pg_catalog.pg_attribute
          WHERE attrelid = pr.prrelid AND attnum = prattrs[s])
        ELSE NULL END) FROM pg_catalog.pg_publication p
     JOIN pg_catalog.pg_publication_rel pr ON p.oid = pr.prpubid
     JOIN pg_catalog.pg_class c ON c.oid = pr.prrelid
WHERE pr.prrelid = {}
UNION
SELECT pubname
     , NULL
     , NULL
FROM pg_catalog.pg_publication p
WHERE p.puballtables AND pg_catalog.pg_relation_is_publishable({})
ORDER BY 1;
""").format(Literal(table.oid), Literal(table.oid), Literal(table.oid), Literal(table.oid))

    return Query(sql)


def select_replication_lag_for_all_slots_query() -> Query:
    sql: Composed = SQL("""
SELECT
    slot_name,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) AS lag_size
FROM pg_replication_slots
ORDER BY lag_size DESC;
""").format()

    return Query(sql)


def select_replication_lag_for_slot_query(slot_name: str) -> Query:
    sql: Composed = SQL("""
SELECT
    slot_name,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) AS lag_size
FROM pg_replication_slots
WHERE slot_name = {};
""").format(Literal(slot_name))

    return Query(sql)


def select_subscription_sync_state_for_all_subscriptions_query() -> Query:
    sql: Composed = SQL("""
SELECT
    s.subname AS subscription_name,
    sr.srrelid::regclass AS table_name,
    sr.srsubstate AS sync_state,
    CASE sr.srsubstate
        WHEN 'i' THEN 'Initialize'
        WHEN 'd' THEN 'Data copy in progress'
        WHEN 's' THEN 'Synchronized'
        WHEN 'r' THEN 'Ready (streaming)'
        ELSE 'Unknown'
    END AS state_description
FROM pg_subscription_rel sr
JOIN pg_subscription s ON s.oid = sr.srsubid
ORDER BY s.subname, sr.srrelid::regclass::text;
""").format()

    return Query(sql)


def select_subscription_sync_state_for_subscription_query(subscription: str) -> Query:
    sql: Composed = SQL("""
SELECT
    s.subname AS subscription_name,
    sr.srrelid::regclass AS table_name,
    sr.srsubstate AS sync_state,
    CASE sr.srsubstate
        WHEN 'i' THEN 'Initialize'
        WHEN 'd' THEN 'Data copy in progress'
        WHEN 's' THEN 'Synchronized'
        WHEN 'r' THEN 'Ready (streaming)'
        ELSE 'Unknown'
    END AS state_description
FROM pg_subscription_rel sr
JOIN pg_subscription s ON s.oid = sr.srsubid
WHERE s.subname = {}
ORDER BY s.subname, sr.srrelid::regclass::text;
""").format(Literal(subscription))

    return Query(sql)
