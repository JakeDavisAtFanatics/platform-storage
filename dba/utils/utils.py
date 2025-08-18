import logging
import os
import sys
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar, cast

import typer
from rich.console import Console
from rich.table import Table

from dba.models import Response, Row

logger = logging.getLogger(__name__)

# Used with exit_on_error() decorator
P = ParamSpec("P")
R = TypeVar("R")


def cleanup_and_exit(message_or_object: Any, cleanup_tasks: Callable[[], None] | None = None) -> None:
    """Print the error message (or object), execute cleanup tasks (if any), then raise exit."""
    logger.error(message_or_object)
    if cleanup_tasks:
        logger.info("Cleaning up...")
        cleanup_tasks()
    else:
        logger.info("No cleanup tasks.")
    raise typer.Exit(code=1)


def exit_on_error(func: Callable[P, Response[R]]) -> Callable[P, Response[R]]:
    """Decorator: Wraps a function call that returns a Response.

    If the Response has an error, look for "cleanup_tasks" to execute and then exit.

    Otherwise, return the Response.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Response[R]:
        cleanup_tasks = cast(Callable[[], None] | None, kwargs.pop("cleanup_tasks", None))
        response: Response[R] = func(*args, **kwargs)
        if response.has_error:
            cleanup_and_exit(response, cleanup_tasks=cleanup_tasks)
        return response

    return wrapper


def goodbye(cleanup_tasks: Callable[[], None] | None = None) -> None:
    if cleanup_tasks:
        logger.info("Cleaning up...")
        cleanup_tasks()
    else:
        logger.info("No cleanup tasks.")
    logger.info("Goodbye 👋")


def pg_conn_string_from_env_vars(database: str = "postgres") -> str:
    required_env_vars = ["PGHOST", "PGPORT", "PGUSER", "PGPASSWORD"]
    missing = [var for var in required_env_vars if not os.getenv(var)]
    if missing:
        for var in missing:
            logger.error(f"Environment variable not set: {var}")
        sys.exit(1)
    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT")
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    logger.info(f"PGHOST={host}")
    logger.info(f"PGPORT={port}")
    logger.info(f"PGUSER={user}")
    logger.info("PGPASSWORD=***")
    logger.info(f"Database={database}")
    return f"user={user} host={host} password={password} port={port} dbname={database}"


def print_table_from_rows(rows: list[Row], title: str | None = None) -> None:
    console = Console()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    console.print(f"\n[dim]{timestamp}[/dim] [yellow]{title}[/yellow]")
    if not rows:
        console.print("[yellow]No data to display.[/yellow]")
        return
    table = Table(show_header=True, header_style="bold magenta")
    for column in rows[0].columns():
        table.add_column(column)
    for row in rows:
        table.add_row(*[str(val) if val is not None else "" for val in row.values()])
    console.print(table)
