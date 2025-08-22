from pydantic import BaseModel, Field


class PartmanConfig(BaseModel):
    primary_key: list[str] = Field(..., description="The new Primary Key which includes the partition column.")
    control: str = Field(..., description="The column to partition on.")
    partition_interval: str = Field(..., description="Partitioning interval (ex: '1 mon').")
    partition_type: str = Field(..., description="Partitioning type (ex: 'range').")
    premake: int = Field(..., description="Number of future partitions to premake.")
    retention: str = Field(..., description="Number of past partitions to retain (ex: 6 months).")
    retention_keep_table: bool = Field(..., description="If true, keep partitions > retention; if false, drop them.")
    start_partition: str = Field(..., description="Partition to start (ex: '6 months').")