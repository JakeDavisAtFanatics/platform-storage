import os
from dataclasses import dataclass, field
from typing import List

from pst.configs.config import get_config

globals = get_config()


@dataclass
class PgPassEntry:
    hostname: str
    port: int
    database: str
    username: str
    password: str

    def to_string(self):
        return f"{self.hostname}:{self.port}:{self.database}:{self.username}:{self.password}"


@dataclass
class PgPassFile:
    entries: List[PgPassEntry] = field(default_factory=list)

    def append_entry(self, entry: PgPassEntry):
        if not isinstance(self.entries, list):
            self.entries = []
        self.entries.append(entry)

    def write_entries_to_file(self):
        with open(globals.pg_pass_file, "w") as f:
            for entry in self.entries:
                f.write(f"{entry.to_string()}\n")
        os.chmod(globals.pg_pass_file, 0o600)
