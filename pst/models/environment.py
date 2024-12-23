from dataclasses import dataclass, field
from typing import Dict, List

from pst.models.database_instance import DatabaseInstance


@dataclass
class Environment:
    name: str
    aws_account_name: str
    aws_region: str
    aws_profile_name: str = field(init=False)
    database_instances: List[DatabaseInstance] = field(default_factory=list)

    def __post_init__(
        self,
        aws_iam_role: str = "AdministratorAccess",
        database_instance_name: str = None,
    ):
        if not database_instance_name:
            database_instance_name = f"{self.name}-postgresql"

        self.aws_profile_name = f"{self.aws_account_name}.{aws_iam_role}"
        self.database_instances = [DatabaseInstance(name=database_instance_name)]

    def update_database_instances(self, database_instances: List[DatabaseInstance]):
        self.database_instances = database_instances

    def to_yaml(self) -> Dict:
        return {
            # "name": self.name, # Not including here as "name" is already the key for these values in Stage.to_yaml()
            "aws_account_name": self.aws_account_name,
            "aws_region": self.aws_region,
            "aws_profile_name": self.aws_profile_name,
            "database_instances": {instance.name: instance.to_yaml() for instance in self.database_instances},
        }
