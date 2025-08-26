from psycopg.sql import SQL, Composed, Identifier

from dba.common.data_types.query import Query
from dba.models.postgres_table_model import PostgresTable


def create_table_like_query(source_table: PostgresTable, target_table: PostgresTable) -> Query:
    sql: Composed = SQL("CREATE TABLE {}.{} (LIKE {}.{});").format(
        Identifier(target_table.schema_),
        Identifier(target_table.name),
        Identifier(source_table.schema_),
        Identifier(source_table.name),
    )

    return Query(sql)

# hardcoded sadness
def drop_constraint_query(table: PostgresTable, constraint_name: str) -> Query:
    sql: Composed = SQL("ALTER TABLE {}.{} DROP CONSTRAINT {};").format(
        Identifier(table.schema_),
        Identifier(table.name),
        Identifier(constraint_name),
    )

    return Query(sql)

def drop_primary_key_query(table: PostgresTable) -> Query:
    sql: Composed = SQL("ALTER TABLE {}.{} DROP CONSTRAINT {};").format(
        Identifier(table.schema_),
        Identifier(table.name),
        Identifier(table.primary_key_name),
    )

    return Query(sql)


def drop_table_if_exists_query(table: PostgresTable) -> Query:
    sql: Composed = SQL("DROP TABLE IF EXISTS {}.{};").format(
        Identifier(table.schema_),
        Identifier(table.name),
    )

    return Query(sql)

def lock_table(table: PostgresTable) -> Query:
    sql: Composed = SQL("ALTER TABLE {}.{} DROP CONSTRAINT {};").format(
        Identifier(table.schema_),
        Identifier(table.name),
        Identifier(table.primary_key_name),
    )

    return Query(sql)

def rename_table_query(source_table: PostgresTable, target_table: PostgresTable) -> Query:
    sql: Composed = SQL("ALTER TABLE {}.{} RENAME TO {};").format(
        Identifier(source_table.schema_),
        Identifier(source_table.name),
        Identifier(target_table.name),
    )

    return Query(sql)
