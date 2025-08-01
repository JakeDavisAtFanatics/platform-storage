import logging
import os
import sys
from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg import Cursor
from psycopg.rows import TupleRow

from postgres_dba.common.data_types import Query
from postgres_dba.models.response_model import Response
from postgres_dba.models.row_model import Row

logger = logging.getLogger(__name__)


class SQLBuilder:
    def __init__(self, conn_info: str):
        self._conn_info = conn_info

    def sql(self, query: Query) -> "SQLExecuter":
        return SQLExecuter(self._conn_info, query)

    @contextmanager
    def get_cursor(self, name: str | None = None, autocommit: bool = False) -> Iterator[Cursor]:
        with psycopg.connect(self._conn_info, autocommit=autocommit) as conn:
            # Named cursors are server-side, use for iterating over large tables
            # Unnamed cursors are client-side
            cursor_factory = conn.cursor(name=name) if name else conn.cursor()
            with cursor_factory as cur:
                yield cur


class SQLExecuter:
    def __init__(self, conn_info: str, query: Query):
        self._conn_info = conn_info
        self._query = query

    def execute(self, cur: Cursor | None = None) -> Response[None]:
        self._log_sql(self._query)

        try:
            if cur:
                cur.execute(self._query)
            else:
                with psycopg.connect(self._conn_info) as conn, conn.cursor() as cur:
                    cur.execute(self._query)

            return Response[None].success(request="execute()")

        except Exception as e:
            return Response[None].failure(
                message="Could not execute query",
                request="handy",
                error=e,
            )

    def fetch(self, cur: Cursor | None = None, batch_size: int | None = None) -> Response[list[Row]]:
        self._log_sql(self._query)

        def _run(cur: Cursor) -> list[Row]:
            cur.execute(self._query)
            tuple_rows: list[TupleRow] = cur.fetchmany(batch_size) if batch_size else cur.fetchall()
            return Row.list_from_tuple_rows(cur, tuple_rows)

        try:
            if cur:
                rows = _run(cur)
            else:
                with psycopg.connect(self._conn_info) as conn:
                    with conn.cursor() as new_cur:
                        rows = _run(new_cur)
            return Response[list[Row]].success(data=rows, request=f"fetch(batch_size={batch_size})")
        except Exception as e:
            return Response[list[Row]].failure(
                message="Could not execute query",
                request="handy",
                error=e,
            )

    def fetch_one(self, cur: Cursor | None = None) -> Response[Row]:
        self._log_sql(self._query)

        def _run(cur: Cursor) -> Row:
            cur.execute(self._query)
            tuple_row: TupleRow | None = cur.fetchone()
            return Row.from_tuple_row(cur, tuple_row)

        try:
            if cur:
                row = _run(cur)
            else:
                with psycopg.connect(self._conn_info) as conn:
                    with conn.cursor() as new_cur:
                        row = _run(new_cur)
            return Response[Row].success(data=row, request="fetch_one()")
        except Exception as e:
            return Response[Row].failure(
                message="Could not execute query",
                request="fetch_one()",
                error=e,
            )

    def _log_sql(self, sql: Query) -> None:
        from textwrap import dedent

        logger.debug(dedent(sql.as_string()))


###########
# Helpers #
###########


def get_pg_conn_info(database: str) -> str:
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
