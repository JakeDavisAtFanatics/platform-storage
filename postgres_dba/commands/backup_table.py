import logging
from typing import Annotated, Any

import typer

from postgres_dba.common.data_types import Query
from postgres_dba.common.queries import (
    drop_table_if_exists_sql,
    insert_into_sql,
    select_all_sql,
    select_column_count_sql,
)
from postgres_dba.common.queries.ddl import create_table_like_sql
from postgres_dba.models.postgres_table_model import PostgresTable
from postgres_dba.models.response_model import Response
from postgres_dba.models.row_model import Row
from postgres_dba.services.sql_builder import SQLBuilder, get_pg_conn_info
from postgres_dba.utils.utils import exit_if_error, extract_values_from_row

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


# Todo     _exit_if_error(response)
# TOdo simiply response.data handling
# Todo debug


@app.callback()
def main(
    table_option: Annotated[str, typer.Option("--table", "-t", help="Name of table.")],
    database_option: Annotated[str, typer.Option("--database", "-d", help="Name of database.")] = "postgres",
    schema_option: Annotated[str, typer.Option("--schema", "-s", help="Name of schema.")] = "public",
    version: Annotated[
        int,
        typer.Option(
            "--version",
            "-v",
            help="Version number to append to the backup table name (e.g. src_table_backup_1.)",
        ),
    ] = 1,
    batch_size: Annotated[
        int, typer.Option("--batch-size", "-b", help="Maximum number of rows to insert per batch.")
    ] = 2500,
    debug: Annotated[bool, typer.Option("--debug", help="Print excessive messages.")] = False,
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

    source_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=table_option,
    )
    target_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=f"{source_table.name}_backup_{version}",
        safe_to_drop=True,
    )
    pg: SQLBuilder = SQLBuilder(get_pg_conn_info(database_option))
    _create_target_table(pg, source_table, target_table)
    column_count: int = _get_column_count(pg, target_table)
    target_table.update_column_count(column_count)
    _populate_target_table(pg, source_table, target_table, batch_size)
    _on_success(source_table.name, target_table.name)


def _create_target_table(pg: SQLBuilder, source_table: PostgresTable, target_table: PostgresTable) -> None:
    query: Query = create_table_like_sql(source_table, target_table)
    response: Response[None] = pg.sql(query).execute()
    exit_if_error(response)


def _get_column_count(pg: SQLBuilder, table: PostgresTable) -> int:
    query: Query = select_column_count_sql(table)
    response: Response[Row] = pg.sql(query).fetch_one()

    def drop_table():
        _drop_target_table(pg, table)

    exit_if_error(response, on_error=drop_table)

    if not response.data:
        logger.error(f"No data returned for column count on {table}.")
        drop_table()
        raise typer.Exit(code=1)

    column_count = next(iter(response.data.values()))

    if column_count == 0:
        logger.error(f"Column count for {table} is 0.")
        drop_table()
        raise typer.Exit(code=1)

    return column_count


def _populate_target_table(
    pg: PostgresService,
    source_table: PostgresTable,
    target_table: PostgresTable,
    batch_size: int,
) -> None:
    batch_number: int = 0

    try:
        select_query: Query = select_all_sql(source_table)
        insert_query: Query = insert_into_sql(target_table)

        # Server-side cursor "read_cur" does not support batch inserts.
        # This is why we create another client-side "write_cur".
        with pg.get_cursor(name=f"backup-table-{source_table}") as read_cur:
            read_cur.execute(select_query)
            with pg.get_cursor(autocommit=True) as write_cur:
                while True:
                    batch_number += 1
                    response: Response[list[Row]] = pg.fetch_many_using_cursor(read_cur, batch_size)

                    if response.has_error:
                        logger.error(response)
                        _drop_target_table(pg, target_table)
                        raise typer.Exit(code=1)

                    if not response.data:
                        logger.info("No more rows to process.")
                        break

                    rows: list[list[Any]] = [extract_values_from_row(row) for row in response.data]
                    logger.info(f"Batch {batch_number} inserting {len(rows)} rows.")
                    write_cur.executemany(insert_query, rows)
    except Exception as e:
        logger.error(e)
        _drop_target_table(pg, target_table)
        raise typer.Exit(code=1)


def _on_success(source_table: str, target_table: str) -> None:
    logger.info(f"Successfully backed up: {source_table} -> {target_table}")
    logger.info("Goodbye 👋")


def _drop_target_table(pg: PostgresService, table: PostgresTable) -> None:
    if table.safe_to_drop:
        query: Query = drop_table_if_exists_sql(table)
        response: Response[None] = pg.execute_and_close_conn(query)

        if response.has_error:
            logger.error(response)
    else:
        logger.error(f"Not dropping table {table.name}. safe_to_drop is False.")


if __name__ == "__main__":
    app()
