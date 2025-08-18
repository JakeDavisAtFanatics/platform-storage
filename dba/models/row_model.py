from typing import Any, Dict, List

from psycopg import Cursor
from pydantic import BaseModel


class Row(BaseModel):
    """Wrapper around a dictionary representing a SQL row."""

    def __init__(self, data: Dict[str, Any]):
        self._data: Dict[str, Any] = data

    @classmethod
    def from_tuple_row(cls, cur: Cursor, row: tuple | None) -> "Row":
        """Create a Row from psycopg fetch_one."""
        if row:
            columns = [desc.name for desc in cur.description] if cur.description else []
            return cls(dict(zip(columns, row)))
        return cls({})

    @classmethod
    def from_tuple_rows(cls, cur: Cursor, rows: List[tuple]) -> List["Row"]:
        """Create a list of Rows from psycopg fetch_all or fetch_many."""
        columns = [desc.name for desc in cur.description] if cur.description else []
        return [cls(dict(zip(columns, row))) for row in rows]

    def get_value(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def columns(self) -> list[str]:
        return list(self._data.keys())

    def values(self) -> list[Any]:
        return list(self._data.values())
