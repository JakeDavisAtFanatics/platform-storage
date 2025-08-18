import logging
from typing import Annotated

import typer

from dba.common.sql import (
    Query,
    select_subscription_sync_state_for_all_subscriptions_query,
    select_subscription_sync_state_for_subscription_query,
)
from dba.services import PostgresService
from dba.utils import goodbye, pg_conn_string_from_env_vars

app = typer.Typer(invoke_without_command=True)
logger = logging.getLogger(__name__)


@app.callback()
def main(
    database_option: Annotated[str, typer.Option("--database", "-d", help="Name of database.")],
    subscription_option: Annotated[
        str | None,
        typer.Option(
            "--subscription",
            "-s",
            help="Optional; Name of the subscription to watch (e.g., sub_fbg_dev_1nj_to_fbg_dev_1).",
        ),
    ] = None,
    interval_option: Annotated[
        int,
        typer.Option("--interval", "-i", help="Number of seconds to wait between query refreshes."),
    ] = 2,
):
    conn_info: str = pg_conn_string_from_env_vars(database_option)
    pg: PostgresService = PostgresService(conn_info)
    query: Query = _get_query(subscription_option)
    _watch_query(pg, query, interval_option)
    goodbye()


def _get_query(subscription: str | None) -> Query:
    query: Query = (
        select_subscription_sync_state_for_subscription_query(subscription)
        if subscription
        else select_subscription_sync_state_for_all_subscriptions_query()
    )

    return query


def _watch_query(pg: PostgresService, query: Query, interval: int) -> None:
    with pg.get_cursor() as cur:
        pg.query(query).watch_or_exit(cur, interval)


if __name__ == "__main__":
    app()
