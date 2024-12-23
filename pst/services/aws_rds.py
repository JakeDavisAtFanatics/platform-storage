from typing import List

from botocore.exceptions import ClientError

from pst.models.database_instance import DatabaseInstance
from pst.models.environment import Environment


class AwsRdsService:
    def __init__(self, session):
        self.session = session

    def get_rds_instances(
        self,
        environment: Environment,
    ) -> List[DatabaseInstance]:
        try:
            rds_client = self.session.client("rds", region_name=environment.aws_region)
            response = rds_client.describe_db_instances(DBInstanceIdentifier=environment.database_instances[0].name)

            result = []

            if response["DBInstances"]:
                instance = response["DBInstances"][0]
                result.append(
                    DatabaseInstance(
                        name=instance["DBInstanceIdentifier"],
                        endpoint=instance["Endpoint"]["Address"],
                        port=instance["Endpoint"]["Port"],
                    )
                )

                # Check for read replicas
                for replica in instance.get("ReadReplicaDBInstanceIdentifiers", []):
                    replica_response = rds_client.describe_db_instances(DBInstanceIdentifier=replica)
                    if replica_response["DBInstances"]:
                        replica_instance = replica_response["DBInstances"][0]

                        result.append(
                            DatabaseInstance(
                                name=replica_instance["DBInstanceIdentifier"],
                                endpoint=replica_instance["Endpoint"]["Address"],
                                port=replica_instance["Endpoint"]["Port"],
                                primary=False,
                            )
                        )

                return result
            else:
                print(f"No RDS instance found with name: {environment.database_instances[0].name}")
                return None
        except ClientError as e:
            print(f"Error retrieving RDS instance: {e}")
            return None
