from botocore.exceptions import ClientError


class AwsSsmService:
    def __init__(self, session, region):
        self.session = session
        self.region = region

    def get_parameter(
        self,
        parameter_name: str,
        with_decryption: bool = True,
    ) -> str:
        try:
            ssm_client = self.session.client("ssm", region_name=self.region)
            response = ssm_client.get_parameter(
                Name=parameter_name,
                WithDecryption=with_decryption,
            )

            return response["Parameter"]["Value"]
        except ClientError:
            return None
