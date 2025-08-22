import logging
from typing import Annotated, Any, Dict

import typer

from dba.common.data_types.query import Query
from dba.common.sql.crud import insert_into_query, select_all_query
from dba.common.sql.table_info import select_column_count_query
from dba.models.partman_config_model import PartmanConfig
from dba.models.postgres_table_model import PostgresTable
from dba.models.response_model import Response
from dba.models.row_model import Row
from dba.services.postgres_service import PostgresService
from dba.services.yaml_service import YamlService
from dba.utils.utils import cleanup_and_exit, goodbye, pg_conn_string_from_env_vars

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


@app.callback()
def main(
    database_option: Annotated[str, typer.Option("--database", "-d", help="Name of database.")],
    table_option: Annotated[str, typer.Option("--table", "-t", help="Name of table.")],
    schema_option: Annotated[str, typer.Option("--schema", "-s", help="Name of schema.")] = "public",
    batch_size_option: Annotated[
        int, typer.Option("--batch-size", "-b", help="Maximum number of rows to insert per batch.")
    ] = 2500,
    debug_option: Annotated[bool, typer.Option("--debug", help="Print excessive messages.")] = False,
):
    if debug_option:
        logging.getLogger().setLevel(logging.DEBUG)

    # TODO use yaml service in fbg-storage-automation
    yaml: YamlService = YamlService("jdavis.yaml")
    partman_dict: Response[Dict[str, Any]] = yaml.get("partman", "jdavis")
    partman_config: PartmanConfig = PartmanConfig.model_validate(partman_dict)

    conn_info: str = pg_conn_string_from_env_vars(database_option)
    pg: PostgresService = PostgresService(conn_info)
    parent_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=table_option,
    )
    archive_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=f"{parent_table.name}_archive",
    )

    column_count: int = _get_column_count(pg, parent_table)
    parent_table.update_column_count(column_count)
    _populate_target_table(pg, parent_table, archive_table, batch_size=batch_size_option)

    goodbye()


def _get_column_count(pg: PostgresService, table: PostgresTable) -> int:
    query: Query = select_column_count_query(table)
    with pg.get_cursor() as cur:
        pg.query(query).execute_or_exit(cur)
        response: Response[Row] = pg.query(query).fetch_one_or_exit(cur)

    column_count: int = 0

    if response.data:
        column_count = next(iter(response.data.values()))

    if column_count == 0:
        error_message: str = f"Column count for {table.name} is 0."
        cleanup_and_exit(error_message)

    return column_count


def _populate_target_table(
    pg: PostgresService,
    parent_table: PostgresTable,
    archive_table: PostgresTable,
    batch_size: int,
) -> None:
    batch_number: int = 0
    select_query: Query = select_all_query(archive_table)
    insert_query: Query = insert_into_query(parent_table)

    # Server-side cursors do not support batch inserts.
    # This is why we create a separate client-side cursor for the writes.
    with pg.get_cursor(name=f"populate-partition-table-{parent_table.name}") as read_cur:
        pg.query(select_query).execute_or_exit(read_cur)

        with pg.get_cursor(autocommit=True) as write_cur:
            while True:
                batch_number += 1
                response: Response[list[Row]] = pg.query(select_query).fetch_or_exit(read_cur, batch_size)

                if not response.data:
                    logger.info("No more rows to process.")
                    break

                batch_values: list[list[Row]] = [row.values() for row in response.data]
                logger.info(f"Batch {batch_number} inserting {len(batch_values)} rows.")
                pg.query(insert_query).execute_or_exit(write_cur, batch_values)

    logger.info(f"Successfully populated: {parent_table.name} from {archive_table.name}")


if __name__ == "__main__":
    app()
