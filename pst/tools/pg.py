import argparse
import os
import subprocess

from pst.configs.config import get_config
from pst.services.user_prompt import UserPromptService
from pst.services.yaml import YamlService

globals = get_config()


class PG:
    def __init__(
        self,
        stage: str = None,
        environment: str = None,
        instance: str = None,
        user: str = None,
    ):
        self.stage = stage
        self.environment = environment
        self.instance = instance
        self.user = user
        self.stage_file: YamlService = None
        self.endpoint: str = None
        self.port: int = None

    def run(self):
        if not self.stage:
            self.stage = self._get_stage()
        elif self.stage not in self._get_stage_names():
            print(f"Invalid stage: {self.stage}. Exiting.")
            return

        # Now that we have the stage, we can load the stage file
        self.stage_file = YamlService(os.path.join(globals.envs_dir, f"{self.stage}.yaml"))

        if not self.environment:
            self.environment = self._get_environment()
        elif self.environment not in self.stage_file.get_keys("environments"):
            print(f"Invalid environment: {self.environment}. Exiting.")
            return

        if not self.instance:
            self.instance = self._get_instance()
        elif self.instance not in self.stage_file.get_keys("environments", self.environment, "database_instances"):
            print(f"Invalid instance: {self.instance}. Exiting.")
            return

        self._set_instance_info()

        if not self.user:
            if self.endpoint and self.port:
                self.user = self._get_user()
            else:
                print("No endpoint or port found for the selected instance. Exiting.")
                return
        elif self.user not in self.stage_file.get_keys(
            "environments",
            self.environment,
            "database_instances",
            self.instance,
            "database_users",
        ):
            print(f"Invalid user: {self.user}. Exiting.")
            return

        self._connect_to_postgres()

    def _get_stage(self) -> str:
        stages = self._get_stage_names()
        return UserPromptService("Select a stage", stages).get_selection()

    def _get_stage_names(self) -> list:
        return [f.split(".")[0] for f in os.listdir(globals.envs_dir) if f.endswith(".yaml")]

    def _get_environment(self) -> str:
        environments = self.stage_file.get_keys("environments")
        return UserPromptService("Select an environment", environments).get_selection()

    def _get_instance(self) -> str:
        instances = self.stage_file.get_keys(
            "environments",
            self.environment,
            "database_instances",
        )
        instance_names = [instance.split(".")[0] for instance in instances]

        return UserPromptService("Select an instance", instance_names).get_selection()

    def _set_instance_info(self):
        instance_info = self.stage_file.get_value(
            "environments",
            self.environment,
            "database_instances",
            self.instance,
        )
        self.endpoint = instance_info["endpoint"]
        self.port = instance_info["port"]

    def _get_user(self) -> str:
        users = self.stage_file.get_keys(
            "environments",
            self.environment,
            "database_instances",
            self.instance,
            "database_users",
        )
        # Ensure 'postgres' is the first user if it exists
        if "postgres" in users:
            users.remove("postgres")
            users.insert(0, "postgres")

        return UserPromptService("Select a user", users).get_selection()

    def _connect_to_postgres(self):
        psql_command = f"psql -h {self.endpoint} -d postgres -p {self.port} -U {self.user}"

        try:
            print("\nConnecting to Postgres...\n")
            subprocess.run(psql_command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to the database: {e}")


def main():
    parser = argparse.ArgumentParser(description="PostgreSQL Interactive Tool")
    parser.add_argument("stage", nargs="?", help="Stage name")
    parser.add_argument("environment", nargs="?", help="Environment name")
    parser.add_argument("instance", nargs="?", help="Instance name")
    parser.add_argument("user", nargs="?", help="Username")
    args = parser.parse_args()

    pg = PG(args.stage, args.environment, args.instance, args.user)
    try:
        pg.run()
    except KeyboardInterrupt:
        exit(0)


if __name__ == "__main__":
    main()
