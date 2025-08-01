from psycopg.sql import SQL, Composed, Identifier

from postgres_dba.common.data_types import Query
from postgres_dba.models.postgres_table_model import PostgresTable
from postgres_dba.utils.utils import log_sql


def insert_into_sql(table: PostgresTable) -> Query:
    placeholders = SQL(", ").join(SQL("%s") for _ in range(table.column_count))
    sql: Composed = SQL("""
INSERT INTO
    {}.{}
VALUES
    ({});""").format(Identifier(table.schema_), Identifier(table.name), placeholders)

    log_sql("insert_into_sql", sql)

    return Query(sql)


def select_all_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
    *
FROM
    {}.{};""").format(Identifier(table.schema_), Identifier(table.name))

    log_sql("select_all_sql", sql)

    return Query(sql)
