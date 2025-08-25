from psycopg.sql import SQL, Composed, Identifier, Literal

from dba.common.data_types.query import Query
from dba.models.postgres_table_model import PostgresTable


def delete_by_ids_query(table: PostgresTable, ids: list[int]) -> Query:
    sql: Composed = SQL("DELETE FROM {}.{} WHERE id = ANY({});").format(
        Identifier(table.schema_),
        Identifier(table.name),
        Literal(ids),
    )

    return Query(sql)


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


def select_ids_query(table: PostgresTable) -> Query:
    sql: Composed = SQL("SELECT id FROM {}.{}").format(Identifier(table.schema_), Identifier(table.name))

    return Query(sql)
