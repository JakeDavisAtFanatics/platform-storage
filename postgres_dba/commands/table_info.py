import logging
from typing import Annotated

import typer

from postgres_dba.common.data_types import Query, Row
from postgres_dba.common.queries import (
    select_column_definition_sql,
    select_indexes_sql,
    select_referenced_by_foreign_keys_sql,
    select_table_oid_sql,
)
from postgres_dba.common.queries.metadata import (
    select_check_constraints_sql,
    select_foreign_keys_sql,
    select_publications_sql,
    select_table_stats_sql,
    select_triggers_sql,
)
from postgres_dba.models.postgres_table_model import PostgresTable
from postgres_dba.models.response_model import Response
from postgres_dba.services.postgres.helpers import get_postgres_service
from postgres_dba.services.postgres.postgres_service import PostgresService
from postgres_dba.utils.utils import print_table_from_rows

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


@app.callback()
def main(
    table_option: Annotated[str, typer.Option("--table", "-t", help="Name of table.")],
    database_option: Annotated[str, typer.Option("--database", "-d", help="Name of database.")] = "postgres",
    schema_option: Annotated[str, typer.Option("--schema", "-s", help="Name of schema.")] = "public",
    debug: Annotated[bool, typer.Option("--debug", help="Print excessive messages.")] = False,
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    table: PostgresTable = PostgresTable(database=database_option, schema_=schema_option, name=table_option)
    pg: PostgresService = get_postgres_service(table.database)
    oid: int = _get_table_oid(pg, table)
    table.update_oid(oid)
    column_definition: list[Row] = _get_column_definition(pg, table)
    indexes: list[Row] = _get_indexes(pg, table)
    check_constraints: list[Row] = _get_check_constraints(pg, table)
    foreign_keys: list[Row] = _get_foreign_keys(pg, table)
    referenced_by_foreign_keys: list[Row] = _get_referenced_by_foreign_keys(pg, table)
    publications: list[Row] = _get_publications(pg, table)
    triggers: list[Row] = _get_triggers(pg, table)
    table_stats: list[Row] = _get_table_stats(pg, table)
    _print_table_info(
        table,
        table_stats,
        column_definition,
        indexes,
        check_constraints,
        foreign_keys,
        referenced_by_foreign_keys,
        publications,
        triggers,
    )
    _on_success()


def _get_table_oid(pg: PostgresService, table: PostgresTable) -> int:
    query: Query = select_table_oid_sql(table)
    response: Response[Row] = pg.fetch_one_and_close_conn(query)
    _exit_if_error(response)

    oid: int = 0

    if response.data:
        oid = next(iter(response.data.values()))

    if oid == 0:
        logger.error(f"OID for {table} is 0.")
        raise typer.Exit(code=1)

    return oid


def _get_column_definition(pg: PostgresService, table: PostgresTable) -> list[Row]:
    query: Query = select_column_definition_sql(table)
    response: Response[list[Row]] = pg.fetch_all_and_close_conn(query)
    _exit_if_error(response)

    return response.data or []


def _get_indexes(pg: PostgresService, table: PostgresTable) -> list[Row]:
    query: Query = select_indexes_sql(table)
    response: Response[list[Row]] = pg.fetch_all_and_close_conn(query)
    _exit_if_error(response)

    return response.data or []


def _get_check_constraints(pg: PostgresService, table: PostgresTable) -> list[Row]:
    query: Query = select_check_constraints_sql(table)
    response: Response[list[Row]] = pg.fetch_all_and_close_conn(query)
    _exit_if_error(response)

    return response.data or []


def _get_foreign_keys(pg: PostgresService, table: PostgresTable) -> list[Row]:
    query: Query = select_foreign_keys_sql(table)
    response: Response[list[Row]] = pg.fetch_all_and_close_conn(query)
    _exit_if_error(response)

    return response.data or []


def _get_referenced_by_foreign_keys(pg: PostgresService, table: PostgresTable) -> list[Row]:
    query: Query = select_referenced_by_foreign_keys_sql(table)
    response: Response[list[Row]] = pg.fetch_all_and_close_conn(query)
    _exit_if_error(response)

    return response.data or []


def _get_publications(pg: PostgresService, table: PostgresTable) -> list[Row]:
    query: Query = select_publications_sql(table)
    response: Response[list[Row]] = pg.fetch_all_and_close_conn(query)
    _exit_if_error(response)

    return response.data or []


def _get_triggers(pg: PostgresService, table: PostgresTable) -> list[Row]:
    query: Query = select_triggers_sql(table)
    response: Response[list[Row]] = pg.fetch_all_and_close_conn(query)
    _exit_if_error(response)

    return response.data or []


def _get_table_stats(pg: PostgresService, table: PostgresTable) -> list[Row]:
    query: Query = select_table_stats_sql(table)
    response: Response[list[Row]] = pg.fetch_all_and_close_conn(query)
    _exit_if_error(response)

    return response.data or []


def _print_table_info(
    table: PostgresTable,
    table_stats: list[Row],
    column_definitions: list[Row],
    indexes: list[Row],
    check_constraints: list[Row],
    foreign_keys: list[Row],
    referenced_by_foreign_keys: list[Row],
    publications: list[Row],
    triggers: list[Row],
) -> None:
    print_table_from_rows(table_stats, f'Table "{table.fqn}"')
    print_table_from_rows(column_definitions, "Columns")
    print_table_from_rows(indexes, "Indexes")
    print_table_from_rows(check_constraints, "Check Constraints")
    print_table_from_rows(foreign_keys, "Foreign Keys")
    print_table_from_rows(referenced_by_foreign_keys, "Referenced By")
    print_table_from_rows(publications, "Publications")
    print_table_from_rows(triggers, "Triggers")


def _exit_if_error(response: Response) -> None:
    if response.has_error:
        logger.error(response)
        raise typer.Exit(code=1)


def _on_success() -> None:
    logger.info("Goodbye 👋")


if __name__ == "__main__":
    app()
