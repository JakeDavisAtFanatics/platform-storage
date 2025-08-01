import logging
from typing import Annotated

import typer

from postgres_dba.common.data_types import Query
from postgres_dba.common.queries import select_replication_lag_for_all_slots, select_replication_lag_for_slot
from postgres_dba.models.response_model import Response
from postgres_dba.services.postgres.helpers import get_postgres_service
from postgres_dba.services.postgres.postgres_service import PostgresService
from postgres_dba.services.watch_service import WatchService

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


@app.callback()
def main(
    slot_name: Annotated[
        str | None,
        typer.Option(
            "--slot",
            "-s",
            help="Optional; Name of the replication slot to watch (e.g., sub_fbg_dev_1nj_to_fbg_dev_1).",
        ),
    ] = None,
    interval: Annotated[
        int,
        typer.Option("--interval", "-i", help="Number of seconds to wait between query refreshes."),
    ] = 2,
):
    pg: PostgresService = get_postgres_service()
    query: Query = _get_query(slot_name)
    _watch_query(pg, query, interval)
    _on_success()


def _get_query(slot_name: str | None) -> Query:
    query: Query

    if slot_name:
        query = select_replication_lag_for_slot(slot_name)
    else:
        query = select_replication_lag_for_all_slots()

    return query


def _watch_query(pg: PostgresService, query: Query, interval: int) -> None:
    watcher = WatchService(pg, interval)
    response: Response[None] = watcher.watch(query)

    if response.has_error:
        logger.error(response)
        raise typer.Exit(code=1)


def _on_success() -> None:
    logger.info("Goodbye 👋")


if __name__ == "__main__":
    app()
