from pst.models.environment import Environment
from pst.models.stage import Stage


class DevStage(Stage):
    def __init__(self):
        super().__init__(
            name="dev",
            environments=[
                Environment(
                    name="fbg-dev-1",
                    aws_account_name="sportsbook-dev",
                    aws_region="us-west-2",
                ),
                Environment(
                    name="fbg-dev-1-debezium-1",
                    aws_account_name="sportsbook-dev",
                    aws_region="us-west-2",
                ),
                Environment(
                    name="fbg-dev-1-data-1",
                    aws_account_name="sportsbook-dev",
                    aws_region="us-west-2",
                ),
                Environment(
                    name="fbg-dev-1c",
                    aws_account_name="sportsbook-va-1-dev",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-dev-1nj",
                    aws_account_name="sportsbook-dev-child-nj-1",
                    aws_region="us-east-2",
                ),
            ],
        )
