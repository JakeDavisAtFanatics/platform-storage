from dataclasses import dataclass, field
from typing import Dict, List, Optional

from pst.models.database_user import DatabaseUser


@dataclass
class DatabaseInstance:
    name: str
    endpoint: Optional[str] = None
    port: int = 5432
    primary: bool = True
    database_users: List[DatabaseUser] = field(default_factory=list)

    def append_database_user(self, database_user: DatabaseUser):
        if not isinstance(self.database_users, list):
            self.database_users = []
        self.database_users.append(database_user)

    def to_yaml(self) -> Dict:
        return {
            # "name": self.name, # Not including here as "name" is already the key for these values in Environment.to_yaml()
            "endpoint": self.endpoint,
            "port": self.port,
            "primary": self.primary,
            "database_users": {user.username: user.to_yaml() for user in self.database_users},
        }
