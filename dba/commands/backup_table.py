import logging
from typing import Annotated

import typer

from dba.common.data_types.query import Query
from dba.common.sql.crud import insert_into_query, select_all_query
from dba.common.sql.ddl import create_table_like_query, drop_table_if_exists_query
from dba.common.sql.table_info import select_column_count_query
from dba.models.postgres_table_model import PostgresTable
from dba.models.response_model import Response
from dba.models.row_model import Row
from dba.services.postgres_service import PostgresService
from dba.utils.utils import cleanup_and_exit, goodbye, pg_conn_string_from_env_vars

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


@app.callback()
def main(
    table_option: Annotated[str, typer.Option("--table", "-t", help="Name of table.")],
    database_option: Annotated[str, typer.Option("--database", "-d", help="Name of database.")] = "postgres",
    schema_option: Annotated[str, typer.Option("--schema", "-s", help="Name of schema.")] = "public",
    version_option: Annotated[
        int,
        typer.Option(
            "--version",
            "-v",
            help="Version number to append to the backup table name (e.g. src_table_backup_1.)",
        ),
    ] = 1,
    batch_size_option: Annotated[
        int, typer.Option("--batch-size", "-b", help="Maximum number of rows to insert per batch.")
    ] = 2500,
    debug_option: Annotated[bool, typer.Option("--debug", help="Print excessive messages.")] = False,
):
    if debug_option:
        logging.getLogger().setLevel(logging.DEBUG)

    conn_info: str = pg_conn_string_from_env_vars(database_option)
    pg: PostgresService = PostgresService(conn_info)
    source_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=table_option,
    )
    target_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=f"{source_table.name}_backup_{version_option}",
        safe_to_drop=True,
    )
    _create_target_table(pg, source_table, target_table)
    column_count: int = _get_column_count(pg, target_table)
    target_table.update_column_count(column_count)
    _populate_target_table(pg, source_table, target_table, batch_size_option)
    goodbye()


def _create_target_table(pg: PostgresService, source_table: PostgresTable, target_table: PostgresTable) -> None:
    query: Query = create_table_like_query(source_table, target_table)
    with pg.get_cursor() as cur:
        pg.query(query).execute_or_exit(cur)


def _get_column_count(pg: PostgresService, table: PostgresTable) -> int:
    query: Query = select_column_count_query(table)
    with pg.get_cursor() as cur:
        pg.query(query).execute_or_exit(cur, cleanup_tasks=lambda: _drop_target_table(pg, table))
        response: Response[Row] = pg.query(query).fetch_one_or_exit(
            cur,
            cleanup_tasks=lambda: _drop_target_table(pg, table),
        )

    column_count: int = 0

    if response.data:
        column_count = next(iter(response.data.values()))

    if column_count == 0:
        error_message: str = f"Column count for {table.name} is 0."
        cleanup_and_exit(error_message, cleanup_tasks=lambda: _drop_target_table(pg, table))

    return column_count


def _populate_target_table(
    pg: PostgresService,
    source_table: PostgresTable,
    target_table: PostgresTable,
    batch_size: int,
) -> None:
    batch_number: int = 0
    select_query: Query = select_all_query(source_table)
    insert_query: Query = insert_into_query(target_table)

    # Server-side cursors do not support batch inserts.
    # This is why we create a separate client-side cursor for the writes.
    with pg.get_cursor(name=f"backup-table-{source_table.name}") as read_cur:
        pg.query(select_query).execute_or_exit(
            read_cur,
            cleanup_tasks=lambda: _drop_target_table(pg, target_table),
        )

        with pg.get_cursor(autocommit=True) as write_cur:
            while True:
                batch_number += 1
                response: Response[list[Row]] = pg.query(select_query).fetch_or_exit(
                    read_cur,
                    batch_size,
                    cleanup_tasks=lambda: _drop_target_table(pg, target_table),
                )

                if not response.data:
                    logger.info("No more rows to process.")
                    break

                batch_values: list[list[Row]] = [row.values() for row in response.data]
                logger.info(f"Batch {batch_number} inserting {len(batch_values)} rows.")
                pg.query(insert_query).execute_or_exit(
                    write_cur,
                    batch_values,
                    cleanup_tasks=lambda: _drop_target_table(pg, target_table),
                )

    logger.info(f"Successfully backed up: {source_table.name} -> {target_table.name}")


def _drop_target_table(pg: PostgresService, table: PostgresTable) -> None:
    if table.safe_to_drop:
        logger.info(f"Dropping table {table.name}.")
        query: Query = drop_table_if_exists_query(table)
        with pg.get_cursor() as cur:
            pg.query(query).execute_or_exit(cur)
    else:
        logger.error(f"Not dropping table {table.name}. safe_to_drop is False.")


if __name__ == "__main__":
    app()
