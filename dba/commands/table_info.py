import logging
from dataclasses import dataclass
from typing import Annotated

import typer

from dba.common.sql import (
    Query,
    select_check_constraints_query,
    select_column_count_query,
    select_column_definition_query,
    select_foreign_keys_query,
    select_indexes_query,
    select_publications_query,
    select_referenced_by_foreign_keys_query,
    select_table_oid_query,
    select_table_stats_query,
    select_triggers_query,
)
from dba.models import PostgresTable, Response, Row
from dba.services import Cursor, PostgresService
from dba.utils import cleanup_and_exit, goodbye, pg_conn_string_from_env_vars, print_table_from_rows

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


@dataclass
class TableInfo:
    table: "PostgresTable"
    table_stats: list["Row"]
    column_count: int
    column_definitions: list["Row"]
    indexes: list["Row"]
    check_constraints: list["Row"]
    foreign_keys: list["Row"]
    referenced_by_foreign_keys: list["Row"]
    publications: list["Row"]
    triggers: list["Row"]


@app.callback()
def main(
    table_option: Annotated[str, typer.Option("--table", "-t", help="Name of table.")],
    database_option: Annotated[str, typer.Option("--database", "-d", help="Name of database.")] = "postgres",
    schema_option: Annotated[str, typer.Option("--schema", "-s", help="Name of schema.")] = "public",
    debug_option: Annotated[bool, typer.Option("--debug", help="Print excessive messages.")] = False,
):
    if debug_option:
        logging.getLogger().setLevel(logging.DEBUG)

    conn_info: str = pg_conn_string_from_env_vars(database_option)
    pg: PostgresService = PostgresService(conn_info)
    table: PostgresTable = PostgresTable(database=database_option, schema_=schema_option, name=table_option)
    table_oid: int = _get_table_oid(pg, table)
    table.update_oid(table_oid)
    table_info: TableInfo = _get_table_info(pg, table)
    _print_table_info(table_info)
    goodbye()


def _get_table_oid(pg: PostgresService, table: PostgresTable) -> int:
    query: Query = select_table_oid_query(table)
    with pg.get_cursor() as cur:
        pg.query(query).execute_or_exit(cur)
        response: Response[Row] = pg.query(query).fetch_one(cur)

    oid: int = 0

    if response.data:
        oid = next(iter(response.data.values()))

    if oid == 0:
        error_message: str = f"OID for {table} is 0."
        cleanup_and_exit(error_message)

    return oid


def _get_table_info(pg: PostgresService, table: PostgresTable) -> TableInfo:
    with pg.get_cursor() as cur:
        table_stats: list[Row] = _get_table_stats(pg, cur, table)
        column_count: int = _get_column_count(pg, cur, table)
        column_definitions: list[Row] = _get_column_definitions(pg, cur, table)
        indexes: list[Row] = _get_indexes(pg, cur, table)
        check_constraints: list[Row] = _get_check_constraints(pg, cur, table)
        foreign_keys: list[Row] = _get_foreign_keys(pg, cur, table)
        referenced_by_foreign_keys: list[Row] = _get_referenced_by_foreign_keys(pg, cur, table)
        publications: list[Row] = _get_publications(pg, cur, table)
        triggers: list[Row] = _get_triggers(pg, cur, table)

    return TableInfo(
        table=table,
        table_stats=table_stats,
        column_count=column_count,
        column_definitions=column_definitions,
        indexes=indexes,
        check_constraints=check_constraints,
        foreign_keys=foreign_keys,
        referenced_by_foreign_keys=referenced_by_foreign_keys,
        publications=publications,
        triggers=triggers,
    )


def _get_table_stats(pg: PostgresService, cur: Cursor, table: PostgresTable) -> list[Row]:
    query: Query = select_table_stats_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[list[Row]] = pg.query(query).fetch(cur)

    return response.data or []


def _get_column_count(pg: PostgresService, cur: Cursor, table: PostgresTable) -> int:
    query: Query = select_column_count_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[Row] = pg.query(query).fetch_one(cur)

    column_count: int = 0

    if response.data:
        column_count = next(iter(response.data.values()))

    return column_count


def _get_column_definitions(pg: PostgresService, cur: Cursor, table: PostgresTable) -> list[Row]:
    query: Query = select_column_definition_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[list[Row]] = pg.query(query).fetch(cur)

    return response.data or []


def _get_indexes(pg: PostgresService, cur: Cursor, table: PostgresTable) -> list[Row]:
    query: Query = select_indexes_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[list[Row]] = pg.query(query).fetch(cur)

    return response.data or []


def _get_check_constraints(pg: PostgresService, cur: Cursor, table: PostgresTable) -> list[Row]:
    query: Query = select_check_constraints_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[list[Row]] = pg.query(query).fetch(cur)

    return response.data or []


def _get_foreign_keys(pg: PostgresService, cur: Cursor, table: PostgresTable) -> list[Row]:
    query: Query = select_foreign_keys_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[list[Row]] = pg.query(query).fetch(cur)

    return response.data or []


def _get_referenced_by_foreign_keys(pg: PostgresService, cur: Cursor, table: PostgresTable) -> list[Row]:
    query: Query = select_referenced_by_foreign_keys_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[list[Row]] = pg.query(query).fetch(cur)

    return response.data or []


def _get_publications(pg: PostgresService, cur: Cursor, table: PostgresTable) -> list[Row]:
    query: Query = select_publications_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[list[Row]] = pg.query(query).fetch(cur)

    return response.data or []


def _get_triggers(pg: PostgresService, cur: Cursor, table: PostgresTable) -> list[Row]:
    query: Query = select_triggers_query(table)
    pg.query(query).execute_or_exit(cur)
    response: Response[list[Row]] = pg.query(query).fetch(cur)

    return response.data or []


def _print_table_info(table_info: TableInfo) -> None:
    print_table_from_rows(table_info.table_stats, f'Table "{table_info.table.fqn}"')
    print_table_from_rows(table_info.column_definitions, f"Columns (count = {table_info.column_count})")
    print_table_from_rows(table_info.indexes, "Indexes")
    print_table_from_rows(table_info.check_constraints, "Check Constraints")
    print_table_from_rows(table_info.foreign_keys, "Foreign Keys")
    print_table_from_rows(table_info.referenced_by_foreign_keys, "Referenced By")
    print_table_from_rows(table_info.publications, "Publications")
    print_table_from_rows(table_info.triggers, "Triggers")


if __name__ == "__main__":
    app()
