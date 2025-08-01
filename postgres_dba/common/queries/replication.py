from psycopg.sql import SQL, Composed, Literal

from postgres_dba.common.data_types import Query
from postgres_dba.utils.utils import log_sql


def select_replication_lag_for_all_slots() -> Query:
    sql: Composed = SQL("""
SELECT
    slot_name,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) AS lag_size
FROM pg_replication_slots
ORDER BY lag_size DESC;
""").format()

    log_sql("select_replication_lag_for_all_slots", sql)

    return Query(sql)


def select_replication_lag_for_slot(slot_name: str) -> Query:
    sql: Composed = SQL("""
SELECT
    slot_name,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn)) AS lag_size
FROM pg_replication_slots
WHERE slot_name = {};
""").format(Literal(slot_name))

    log_sql("select_replication_lag_for_slot", sql)

    return Query(sql)


def select_subscription_sync_state_for_all_subscriptions() -> Query:
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

    log_sql("select_subscription_sync_state_for_all_subscriptions", sql)

    return Query(sql)


def select_subscription_sync_state_for_subscription(subscription: str) -> Query:
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

    log_sql("select_subscription_sync_state_for_subscription", sql)

    return Query(sql)
