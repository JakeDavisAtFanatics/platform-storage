import logging
from datetime import datetime, timezone
from typing import Any, Callable

import typer
from rich.console import Console
from rich.table import Table

from postgres_dba.models.response_model import Response
from postgres_dba.models.row_model import Row

logger = logging.getLogger(__name__)


def exit_if_error(response: Response, on_error: Callable[[], None] | None = None) -> None:
    if response.has_error:
        if on_error:
            on_error()  # execute cleanup or any other side effect
        logger.error(response)
        raise typer.Exit(code=1)


def extract_values_from_row(row: Row) -> list[Any]:
    values: list[Any] = list(row.values())

    return values


def print_table_from_rows(rows: list[Row], title: str | None = None) -> None:
    console = Console()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    console.print(f"\n[dim]{timestamp}[/dim] [yellow]{title}[/yellow]")

    if not rows:
        console.print("[yellow]No data to display.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")

    for column in rows[0].keys():
        table.add_column(column)

    for row in rows:
        table.add_row(*[str(row[col]) if row[col] is not None else "" for col in row.keys()])

    console.print(table)
