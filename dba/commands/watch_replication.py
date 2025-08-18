import logging
from typing import Annotated

import typer

from dba.common.sql import Query, select_replication_lag_for_all_slots_query, select_replication_lag_for_slot_query
from dba.services import PostgresService
from dba.utils import goodbye, pg_conn_string_from_env_vars

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


@app.callback()
def main(
    slot_name_option: Annotated[
        str | None,
        typer.Option(
            "--slot",
            "-s",
            help="Optional; Name of the replication slot to watch (e.g., sub_fbg_dev_1nj_to_fbg_dev_1). If none, watch all slots.",  # noqa: E501
        ),
    ] = None,
    interval_option: Annotated[
        int,
        typer.Option("--interval", "-i", help="Number of seconds to wait between query refreshes."),
    ] = 2,
):
    conn_info: str = pg_conn_string_from_env_vars()
    pg: PostgresService = PostgresService(conn_info)
    query: Query = _get_query(slot_name_option)
    _watch_query(pg, query, interval_option)
    goodbye()


def _get_query(slot_name: str | None) -> Query:
    query: Query = (
        select_replication_lag_for_slot_query(slot_name) if slot_name else select_replication_lag_for_all_slots_query()
    )

    return query


def _watch_query(pg: PostgresService, query: Query, interval: int) -> None:
    with pg.get_cursor() as cur:
        pg.query(query).watch_or_exit(cur, interval)


if __name__ == "__main__":
    app()
