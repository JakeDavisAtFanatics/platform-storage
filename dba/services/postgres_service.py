import logging
from contextlib import contextmanager
from time import sleep
from typing import Callable, Iterator

import psycopg
from psycopg import Cursor
from psycopg.rows import TupleRow

from dba.common.data_types.query import Query
from dba.models.response_model import Response
from dba.models.row_model import Row
from dba.utils.utils import exit_on_error, print_table_from_rows

logger = logging.getLogger(__name__)


class PostgresService:
    def __init__(self, conn_info: str):
        self._conn_info: str = conn_info

    @contextmanager
    def get_cursor(self, name: str | None = None, autocommit: bool = False) -> Iterator[Cursor]:
        cursor_name: str = name if name else "Client-side"
        with psycopg.connect(self._conn_info, autocommit=autocommit) as conn:
            cursor_factory = conn.cursor(name=name) if name else conn.cursor()
            with cursor_factory as cur:
                logger.debug(f"{cursor_name} cursor opened (autocommit={autocommit}).")
                yield cur
                logger.debug(f"{cursor_name} cursor closed.")

    def query(self, query: Query) -> "_QueryExecutioner":
        return _QueryExecutioner(self._conn_info, query)


class _QueryExecutioner:
    def __init__(self, conn_info: str, query: Query):
        self._conn_info: str = conn_info
        self._query: Query = query

    def execute(self, cur: Cursor, batch_values: list[list[Row]] | None = None) -> Response[None]:
        self._log_query(self._query)

        try:
            cur.executemany(self._query, batch_values) if batch_values else cur.execute(self._query)
            return Response[None].success()
        except Exception as e:
            return Response[None].failure(message="Could not execute query", error=e)

    @exit_on_error
    def execute_or_exit(
        self,
        cur: Cursor,
        batch_values: list[list[Row]] | None = None,
        cleanup_tasks: Callable[[], None] | None = None,
    ) -> Response[None]:
        return self.execute(cur, batch_values=batch_values)

    def fetch(self, cur: Cursor, batch_size: int | None = None) -> Response[list[Row]]:
        try:
            tuple_rows: list[TupleRow] = cur.fetchmany(batch_size) if batch_size else cur.fetchall()
            rows: list[Row] = Row.from_tuple_rows(cur, tuple_rows)
            return Response[list[Row]].success(data=rows)
        except Exception as e:
            return Response[list[Row]].failure(message="Could not fetch rows", error=e)

    @exit_on_error
    def fetch_or_exit(
        self,
        cur: Cursor,
        batch_size: int | None = None,
        cleanup_tasks: Callable[[], None] | None = None,
    ) -> Response[list[Row]]:
        return self.fetch(cur, batch_size)

    def fetch_one(self, cur: Cursor) -> Response[Row]:
        try:
            tuple_row: TupleRow | None = cur.fetchone()
            row: Row = Row.from_tuple_row(cur, tuple_row)
            return Response[Row].success(data=row)
        except Exception as e:
            return Response[Row].failure(message="Could not fetch row", error=e)

    @exit_on_error
    def fetch_one_or_exit(
        self,
        cur: Cursor,
        cleanup_tasks: Callable[[], None] | None = None,
    ) -> Response[Row]:
        return self.fetch_one(cur)

    @exit_on_error
    def watch_or_exit(
        self,
        cur: Cursor,
        interval: int = 2,
        cleanup_tasks: Callable[[], None] | None = None,
    ) -> Response[None]:
        """Watch a query and print results to a table."""
        try:
            while True:
                cur.execute(self._query)
                tuple_rows: list[TupleRow] = cur.fetchall()
                rows: list[Row] = Row.from_tuple_rows(cur, tuple_rows)
                print_table_from_rows(rows)
                sleep(interval)
        except KeyboardInterrupt:
            logger.info("Stopped watching.")
            return Response.success()
        except Exception as e:
            return Response.failure(error=e)

    def _log_query(self, sql: Query) -> None:
        from textwrap import dedent

        sql_str = dedent(sql.as_string())
        max_start = 500
        max_end = 50

        if len(sql_str) > (max_start + max_end):
            truncated = f"{sql_str[:max_start]}...{sql_str[-max_end:]}"
        else:
            truncated = sql_str

        logger.debug(truncated)
