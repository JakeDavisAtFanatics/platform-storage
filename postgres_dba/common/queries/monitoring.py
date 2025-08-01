from psycopg.sql import SQL, Composed, Literal

from postgres_dba.common.data_types import Query
from postgres_dba.utils.utils import log_sql


def select_processlist_for_longest_duration(trim_query: int, limit: int) -> Query:
    sql: Composed = SQL("""
SELECT
    datname AS database,
    usename AS user,
    pid, state,
    GREATEST(now() - xact_start, INTERVAL '0') AS duration,
    LEFT(query, {}) AS query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start ASC LIMIT {};
""").format(Literal(trim_query), Literal(limit))

    log_sql("select_processlist_for_longest_duration", sql)

    return Query(sql)
