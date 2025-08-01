from psycopg.sql import SQL, Composed, Identifier

from postgres_dba.common.data_types import Query
from postgres_dba.models.postgres_table_model import PostgresTable
from postgres_dba.utils.utils import log_sql


def create_table_like_sql(source_table: PostgresTable, target_table: PostgresTable) -> Query:
    sql: Composed = SQL("""
CREATE TABLE
    {}.{} (LIKE {}.{});""").format(
        Identifier(target_table.schema_),
        Identifier(target_table.name),
        Identifier(source_table.schema_),
        Identifier(source_table.name),
    )

    log_sql("create_table_like_sql", sql)

    return Query(sql)


def drop_table_if_exists_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
DROP TABLE IF EXISTS {}.{};""").format(
        Identifier(table.schema_),
        Identifier(table.name),
    )

    log_sql("drop_table_if_exists_sql", sql)

    return Query(sql)
