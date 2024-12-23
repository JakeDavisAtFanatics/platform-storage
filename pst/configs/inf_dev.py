from pst.models.environment import Environment
from pst.models.stage import Stage


class InfDevStage(Stage):
    def __init__(self):
        super().__init__(
            name="inf-dev",
            environments=[
                Environment(
                    name="fbg-inf-dev-1",
                    aws_account_name="sportsbook-inf-dev",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-inf-dev-1-debezium-1",
                    aws_account_name="sportsbook-inf-dev",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-inf-dev-1-data-1",
                    aws_account_name="sportsbook-inf-dev",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-inf-dev-1tn",
                    aws_account_name="sportsbook-inf-dev-child-tn-1",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-inf-dev-1nj",
                    aws_account_name="sportsbook-inf-dev-child-nj-1",
                    aws_region="us-east-2",
                ),
            ],
        )
