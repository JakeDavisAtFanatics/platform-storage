import argparse
import os
from typing import List, Optional

from pst.configs.config import get_config
from pst.models.database_instance import DatabaseInstance
from pst.models.database_user import DatabaseUser
from pst.models.environment import Environment
from pst.models.pg_pass import PgPassEntry, PgPassFile
from pst.models.stage import Stage
from pst.services.aws_rds import AwsRdsService
from pst.services.aws_ssm import AwsSsmService
from pst.services.aws_sso import AwsSsoService
from pst.services.user_prompt import UserPromptService
from pst.services.yaml import YamlService

globals = get_config()

"""TODO: Review local vs remote environment processing"""


class PgInit:
    def __init__(self):
        self.pg_pass_file = PgPassFile(globals.pg_pass_file)

    def run(self):
        os.makedirs(globals.envs_dir, exist_ok=True)
        stage_list = self._get_stage_list()

        for stage in stage_list:
            self._process_stage(stage)

        self.pg_pass_file.write_entries_to_file()

    def _get_stage_list(self) -> List[Stage]:
        stage_names = ["all"] + [stage.name for stage in globals.stages]
        stage_name = UserPromptService("Available stages", stage_names).get_selection()

        if stage_name == "all":
            return globals.stages
        else:
            return [s for s in globals.stages if s.name == stage_name]

    def _process_stage(self, stage: Stage):
        print(f"Processing stage: {stage.name}")

        for environment in stage.environments:
            self._process_environment(environment)

        stage_file = YamlService(os.path.join(globals.envs_dir, f"{stage.name}.yaml"))
        stage_yaml = stage.to_yaml()
        stage_file.write_file(stage_yaml)
        print(f"Updated file: {globals.envs_dir}/{stage.name}.yaml")

    def _process_environment(self, environment: Environment):
        print(f"Processing environment: {environment.name}")
        if environment.name == "local":
            self._process_local_environment(environment)
        else:
            self._process_remote_environment(environment)

    def _process_local_environment(self, environment: Environment):
        for instance in environment.database_instances:
            pg_pass_entry = PgPassEntry(instance.endpoint, instance.port, "*", "postgres", "password")
            self.pg_pass_file.update(pg_pass_entry)
            print(f'Updated pgpass for: "{environment.name}" "{instance.name}"')

    def _process_remote_environment(self, environment: Environment):
        try:
            aws_sso = AwsSsoService()
            aws_sso.authenticate(environment.aws_profile_name)
            session = aws_sso.get_session()
            aws_rds = AwsRdsService(session)
            aws_ssm = AwsSsmService(session, environment.aws_region)
            database_instances = aws_rds.get_rds_instances(environment)

            if database_instances:
                print(f"Found {len(database_instances)} database instances.")
                environment.update_database_instances(database_instances)
                all_database_users = globals.database_users(environment.name)

                for instance in database_instances:
                    self._process_instance(instance, all_database_users, aws_ssm)
            else:
                print("No database instances found.")
                return

        except Exception as e:
            print(f"Error processing environment: {e}")

    def _process_instance(
        self,
        instance: DatabaseInstance,
        database_users: List[DatabaseUser],
        aws_ssm: AwsSsmService,
    ):
        print(f"Checking for users in {instance.name}")

        for user in database_users:
            username = aws_ssm.get_parameter(user.username_parameter_store_path)
            password = aws_ssm.get_parameter(user.password_parameter_store_path)

            if username and password:
                user.update_username(username)
                instance.append_database_user(user)
                pg_pass_entry = PgPassEntry(
                    instance.endpoint,
                    instance.port,
                    "*",
                    username,
                    password,
                )
                self.pg_pass_file.append_entry(pg_pass_entry)
                print(f"Found user {username}.")


def main():
    pg_init = PgInit()
    pg_init.run()


if __name__ == "__main__":
    main()
