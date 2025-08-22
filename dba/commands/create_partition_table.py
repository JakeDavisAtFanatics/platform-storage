import logging
from typing import Annotated, Any, Dict

import typer

from dba.common.data_types.query import Query
from dba.common.sql.ddl import create_table_like_query, drop_primary_key_query, rename_table_query
from dba.common.sql.partition import (
    create_table_like_including_all_partition_by_range_query,
    partman_create_parent_query,
    partman_update_retention_query,
)
from dba.common.sql.table_info import select_primary_key_name_query
from dba.models.partman_config_model import PartmanConfig
from dba.models.postgres_table_model import PostgresTable
from dba.models.response_model import Response
from dba.models.row_model import Row
from dba.services.postgres_service import Cursor, PostgresService
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
    source_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=table_option,
    )
    archive_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=f"{source_table.name}_archive",
    )
    parent_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_=schema_option,
        name=f"{source_table.name}",
        safe_to_drop=True,
        partman_config=partman_config,
    )
    template_table: PostgresTable = PostgresTable(
        database=database_option,
        schema_="partman",
        name=f"{parent_table.name}_template",
        safe_to_drop=True,
    )

    with pg.get_cursor() as cur:
        _rename_source_table_to_archive_table(pg, cur, source_table, archive_table)
        primary_key_name: str = _get_primary_key_name_from_archive_table(pg, cur, archive_table)
        archive_table.update_primary_key_name(primary_key_name)
        _drop_primary_key_from_archive_table(pg, cur, archive_table)
        _create_parent_table(pg, cur, parent_table, archive_table)
        _create_template_table(pg, cur, parent_table, template_table)
        _create_partman_config(pg, cur, parent_table, template_table)
        _update_partman_retention(pg, cur, parent_table)
    goodbye()


def _rename_source_table_to_archive_table(
    pg: PostgresService,
    cur: Cursor,
    source_table: PostgresTable,
    archive_table: PostgresTable,
) -> None:
    query: Query = rename_table_query(source_table, archive_table)
    pg.query(query).execute_or_exit(cur)


def _get_primary_key_name_from_archive_table(
    pg: PostgresService,
    cur: Cursor,
    archive_table: PostgresTable,
) -> str:
    query: Query = select_primary_key_name_query(archive_table)
    pg.query(query).execute_or_exit(cur)
    response: Response[Row] = pg.query(query).fetch_one_or_exit(cur)

    primary_key_name: str = ""

    if response.data:
        primary_key_name = next(iter(response.data.values()))

    if not primary_key_name:
        error_message: str = f"Primary Key name for {archive_table.name} is empty."
        cleanup_and_exit(error_message)

    return primary_key_name


def _drop_primary_key_from_archive_table(
    pg: PostgresService,
    cur: Cursor,
    archive_table: PostgresTable,
) -> None:
    query: Query = drop_primary_key_query(archive_table)
    pg.query(query).execute_or_exit(cur)


def _create_parent_table(
    pg: PostgresService,
    cur: Cursor,
    parent_table: PostgresTable,
    archive_table: PostgresTable,
) -> None:
    query: Query = create_table_like_including_all_partition_by_range_query(archive_table, parent_table)
    pg.query(query).execute_or_exit(cur)


def _create_template_table(
    pg: PostgresService,
    cur: Cursor,
    parent_table: PostgresTable,
    template_table: PostgresTable,
) -> None:
    query: Query = create_table_like_query(parent_table, template_table)
    pg.query(query).execute_or_exit(cur)


def _create_partman_config(
    pg: PostgresService,
    cur: Cursor,
    parent_table: PostgresTable,
    template_table: PostgresTable,
) -> None:
    query: Query = partman_create_parent_query(parent_table, template_table)
    pg.query(query).execute_or_exit(cur)


def _update_partman_retention(
    pg: PostgresService,
    cur: Cursor,
    parent_table: PostgresTable,
) -> None:
    query: Query = partman_update_retention_query(parent_table)
    pg.query(query).execute_or_exit(cur)


if __name__ == "__main__":
    app()
