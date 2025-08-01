import logging
from typing import Annotated

import typer

from postgres_dba.common.data_types import Query
from postgres_dba.common.queries import select_processlist_for_longest_duration
from postgres_dba.models.response_model import Response
from postgres_dba.services.postgres.helpers import get_postgres_service
from postgres_dba.services.postgres.postgres_service import PostgresService
from postgres_dba.services.watch_service import WatchService

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


@app.callback()
def main(
    trim: Annotated[
        int,
        typer.Option("--trim-query", "-t", help="Maximum number of characters to display from each query."),
    ] = 250,
    limit: Annotated[
        int,
        typer.Option("--limit", "-l", help="Maximum number of queries to display."),
    ] = 5,
    interval: Annotated[
        int,
        typer.Option("--interval", "-i", help="Number of seconds to wait between query refreshes."),
    ] = 2,
):
    pg: PostgresService = get_postgres_service()
    query: Query = select_processlist_for_longest_duration(trim, limit)
    _watch_query(pg, query, interval)
    _on_success()


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
