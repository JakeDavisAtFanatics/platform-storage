from pydantic import BaseModel


class Column(BaseModel):
    name: str
    alias: str | None = None

    def sql(self) -> str:
        return f"{self.name} AS {self.alias}" if self.alias else self.name
