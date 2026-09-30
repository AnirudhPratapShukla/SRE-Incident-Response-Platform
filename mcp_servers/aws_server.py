import boto3

from pydantic import BaseModel, Field

from mcp.server import MCPServer


mcp = MCPServer(
    "SRE AWS Read-Only Server",
    description=(
        "Read-only AWS tools for the SRE Incident Response Platform. "
        "These tools do not modify AWS infrastructure."
    ),
)


class EC2Instance(BaseModel):
    instance_id: str | None = None
    instance_type: str | None = None
    state: str | None = None
    private_ip: str | None = None
    public_ip: str | None = None


class EC2InstanceStatus(BaseModel):
    instance_id: str
    found: bool
    instance_state: str | None = None
    system_status: str | None = None
    instance_status: str | None = None
    message: str | None = None


class CloudWatchAlarm(BaseModel):
    alarm_name: str | None = None
    state: str | None = None
    state_reason: str | None = None
    metric_name: str | None = None
    namespace: str | None = None
    dimensions: list[dict] = Field(default_factory=list)


def get_ec2_client():
    return boto3.client("ec2")


def get_cloudwatch_client():
    return boto3.client("cloudwatch")


@mcp.tool()
def list_ec2_instances() -> list[EC2Instance]:
    """List EC2 instances and their current state."""

    ec2 = get_ec2_client()

    response = ec2.describe_instances()

    instances = []

    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instances.append(
                EC2Instance(
                    instance_id=instance.get("InstanceId"),
                    instance_type=instance.get("InstanceType"),
                    state=instance.get("State", {}).get("Name"),
                    private_ip=instance.get("PrivateIpAddress"),
                    public_ip=instance.get("PublicIpAddress"),
                )
            )

    return instances


@mcp.tool()
def get_ec2_instance_status(
    instance_id: str,
) -> EC2InstanceStatus:
    """Get the current status of a specific EC2 instance."""

    ec2 = get_ec2_client()

    response = ec2.describe_instance_status(
        InstanceIds=[instance_id],
        IncludeAllInstances=True,
    )

    statuses = response.get("InstanceStatuses", [])

    if not statuses:
        return EC2InstanceStatus(
            instance_id=instance_id,
            found=False,
            message="No EC2 status information found.",
        )

    status = statuses[0]

    return EC2InstanceStatus(
        instance_id=instance_id,
        found=True,
        instance_state=status.get(
            "InstanceState", {}
        ).get("Name"),
        system_status=status.get(
            "SystemStatus", {}
        ).get("Status"),
        instance_status=status.get(
            "InstanceStatus", {}
        ).get("Status"),
    )


@mcp.tool()
def get_cloudwatch_alarms() -> list[CloudWatchAlarm]:
    """List CloudWatch alarms currently in ALARM state."""

    cloudwatch = get_cloudwatch_client()

    response = cloudwatch.describe_alarms(
        StateValue="ALARM"
    )

    alarms = []

    for alarm in response.get("MetricAlarms", []):
        alarms.append(
            CloudWatchAlarm(
                alarm_name=alarm.get("AlarmName"),
                state=alarm.get("StateValue"),
                state_reason=alarm.get("StateReason"),
                metric_name=alarm.get("MetricName"),
                namespace=alarm.get("Namespace"),
                dimensions=alarm.get("Dimensions", []),
            )
        )

    return alarms


if __name__ == "__main__":
    mcp.run()