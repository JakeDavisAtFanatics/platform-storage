from typing import NewType

from psycopg.sql import Composed

Query = NewType("Query", Composed)
