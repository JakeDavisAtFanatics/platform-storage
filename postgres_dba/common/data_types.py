from typing import Any, NewType

from psycopg.sql import Composed

Query = NewType("Query", Composed)
#Row = NewType("Row", dict[str, Any])
