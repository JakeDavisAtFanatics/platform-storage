from typing import Any

from psycopg import Cursor
from psycopg.rows import TupleRow
from pydantic import BaseModel


class Row(BaseModel):
    def __init__(self, data: dict[str, Any] = {}):
        self._data = data

    def __bool__(self) -> bool:
        return bool(self._data)

    @classmethod
    def from_tuple_row(cls, cursor: Cursor, row: TupleRow | None) -> "Row":
        if row:
            columns = [desc.name for desc in cursor.description] if cursor.description else []
            return cls(dict(zip(columns, row)))

        return cls({})

    @classmethod
    def list_from_tuple_rows(cls, cursor: Cursor, rows: list[TupleRow]) -> list["Row"]:
        columns = [desc.name for desc in cursor.description] if cursor.description else []
        return [cls(dict(zip(columns, row))) for row in rows]

    def values(self):
        return self._data.values()
