from pst.models.environment import Environment
from pst.models.stage import Stage


class TestStage(Stage):
    def __init__(self):
        super().__init__(
            name="test",
            environments=[
                Environment(
                    name="fbg-test-1",
                    aws_account_name="sportsbook-test",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-test-1-debezium-1",
                    aws_account_name="sportsbook-test",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-test-1-data-1",
                    aws_account_name="sportsbook-test",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-test-1c",
                    aws_account_name="sportsbook-test-child-1",
                    aws_region="us-east-2",
                ),
                Environment(
                    name="fbg-test-1tn",
                    aws_account_name="sportsbook-test-child-tn-1",
                    aws_region="us-east-1",
                ),
                Environment(
                    name="fbg-test-1nj",
                    aws_account_name="sportsbook-test-child-nj-1",
                    aws_region="us-east-1",
                ),
            ],
        )
