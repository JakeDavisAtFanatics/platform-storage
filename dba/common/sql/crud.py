from psycopg.sql import SQL, Composed, Identifier

from dba.common.sql import Query
from dba.models import PostgresTable


def insert_into_query(table: PostgresTable) -> Query:
    placeholders = SQL(", ").join(SQL("%s") for _ in range(table.column_count))
    sql: Composed = SQL("INSERT INTO {}.{} VALUES({});").format(
        Identifier(table.schema_),
        Identifier(table.name),
        placeholders,
    )

    return Query(sql)


def select_all_query(table: PostgresTable) -> Query:
    sql: Composed = SQL("SELECT * FROM {}.{};").format(Identifier(table.schema_), Identifier(table.name))

    return Query(sql)
