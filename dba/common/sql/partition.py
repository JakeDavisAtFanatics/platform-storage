from typing import LiteralString, cast

from psycopg.sql import SQL, Composed, Identifier, Literal

from dba.common.data_types.query import Query
from dba.models.postgres_table_model import PostgresTable


def create_table_like_including_all_partition_by_range_query(
    source_table: PostgresTable,
    target_table: PostgresTable,
) -> Query:
    if target_table.partman_config is None:
        raise ValueError(f"Table {target_table.name} has no PartmanConfig set.")

    primary_key: Composed = SQL(", ").join([Identifier(k) for k in target_table.partman_config.primary_key])

    sql: Composed = SQL("""
CREATE TABLE
    {}.{} (
        LIKE {}.{} INCLUDING ALL,
        PRIMARY KEY ({})
    )
PARTITION BY
    RANGE ({});
""").format(
        Identifier(target_table.schema_),
        Identifier(target_table.name),
        Identifier(source_table.schema_),
        Identifier(source_table.name),
        primary_key,
        Identifier(target_table.partman_config.control),
    )

    return Query(sql)


def partman_create_parent_query(parent_table: PostgresTable, template_table: PostgresTable) -> Query:
    if parent_table.partman_config is None:
        raise ValueError(f"Table {parent_table.name} has no PartmanConfig set.")

    start_partition: LiteralString = cast(LiteralString, parent_table.partman_config.start_partition)

    sql: Composed = SQL("""
SELECT partman.create_parent(
    p_parent_table := {},
    p_control := {},
    p_interval := {},
    p_type := {},
    p_premake := {},
    p_start_partition := {},
    p_template_table := {});
""").format(
        Literal(parent_table.fqn),
        Literal(parent_table.partman_config.control),
        Literal(parent_table.partman_config.partition_interval),
        Literal(parent_table.partman_config.partition_type),
        Literal(parent_table.partman_config.premake),
        SQL(start_partition),
        Literal(template_table.fqn),
    )

    return Query(sql)


def partman_update_retention_query(table: PostgresTable) -> Query:
    if table.partman_config is None:
        raise ValueError(f"Table {table.name} has no PartmanConfig set.")

    sql: Composed = SQL(
        "UPDATE partman.part_config SET retention = {}, retention_keep_table = {} WHERE parent_table = {};"
    ).format(
        Literal(table.partman_config.retention),
        Literal(table.partman_config.retention_keep_table),
        Literal(table.fqn),
    )

    return Query(sql)
