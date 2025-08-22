from pydantic import BaseModel

from dba.models.partman_config_model import PartmanConfig


class PostgresTable(BaseModel):
    oid: int = 0
    database: str
    schema_: str  # "schema" is already a BaseModel method so we need to append an underscore
    name: str
    safe_to_drop: bool = False
    column_count: int = 0
    primary_key_name: str = ""
    partman_config: PartmanConfig | None = None

    @property
    def fqn(self) -> str:
        return f"{self.schema_}.{self.name}"

    def update_column_count(self, new_column_count: int) -> None:
        self.column_count = new_column_count

    def update_primary_key_name(self, new_primary_key_name: str) -> None:
        self.primary_key_name = new_primary_key_name

    def update_oid(self, new_oid: int) -> None:
        self.oid = new_oid
