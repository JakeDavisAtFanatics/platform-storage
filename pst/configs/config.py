import os
from dataclasses import dataclass, field
from typing import List

from pst.configs.cert import CertStage
from pst.configs.dev import DevStage
from pst.configs.inf_dev import InfDevStage
from pst.configs.prod import ProdStage
from pst.configs.test import TestStage
from pst.models.database_user import DatabaseUser
from pst.models.stage import Stage


@dataclass
class Config:
    envs_dir: str = field(default_factory=lambda: os.path.expanduser("~/.pst/envs"))
    pg_pass_file: str = field(default_factory=lambda: os.path.expanduser("~/.pgpass"))
    stages: List[Stage] = field(
        default_factory=lambda: [
            DevStage(),
            InfDevStage(),
            TestStage(),
            CertStage(),
            ProdStage(),
        ]
    )

    @staticmethod
    def database_users(environment_name: str) -> List[DatabaseUser]:
        return [
            # postgres user
            DatabaseUser(
                username_parameter_store_path=f"/{environment_name}/database/master-user",
                password_parameter_store_path=f"/{environment_name}/database/master-pass",
            ),
            DatabaseUser(
                username_parameter_store_path=f"/{environment_name}/database/replication/username",
                password_parameter_store_path=f"/{environment_name}/database/replication/password",
            ),
            DatabaseUser(
                username_parameter_store_path=f"/{environment_name}/database/debezium_nj/username",
                password_parameter_store_path=f"/{environment_name}/database/debezium_nj/password",
            ),
        ]


config: Config = Config()


def get_config() -> Config:
    return config
