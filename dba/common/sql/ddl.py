from psycopg.sql import SQL, Composed, Identifier

from dba.common.sql import Query
from dba.models import PostgresTable


def create_table_like_query(source_table: PostgresTable, target_table: PostgresTable) -> Query:
    sql: Composed = SQL("CREATE TABLE {}.{} (LIKE {}.{});").format(
        Identifier(target_table.schema_),
        Identifier(target_table.name),
        Identifier(source_table.schema_),
        Identifier(source_table.name),
    )

    return Query(sql)


def drop_table_if_exists_query(table: PostgresTable) -> Query:
    sql: Composed = SQL("DROP TABLE IF EXISTS {}.{};").format(
        Identifier(table.schema_),
        Identifier(table.name),
    )

    return Query(sql)
