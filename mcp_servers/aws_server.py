import re

import boto3

from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

from mcp.server import MCPServer


mcp = MCPServer(
    "SRE AWS Controlled Server",
    description=(
        "AWS tools for the SRE Incident Response Platform. "
        "Read operations are available for investigation. "
        "AWS-changing operations require explicit approval "
        "and controlled execution."
    ),
)


# ============================================================
# RESPONSE MODELS
# ============================================================

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


class EC2RebootResult(BaseModel):
    instance_id: str
    approved: bool
    dry_run: bool
    executed: bool
    success: bool
    message: str


# ============================================================
# AWS CLIENTS
# ============================================================

def get_ec2_client():
    return boto3.client("ec2")


def get_cloudwatch_client():
    return boto3.client("cloudwatch")


# ============================================================
# READ-ONLY TOOLS
# ============================================================

@mcp.tool()
def list_ec2_instances() -> list[EC2Instance]:
    """List EC2 instances and their current state."""

    ec2 = get_ec2_client()

    response = ec2.describe_instances()

    instances = []

    for reservation in response.get(
        "Reservations",
        []
    ):

        for instance in reservation.get(
            "Instances",
            []
        ):

            instances.append(
                EC2Instance(
                    instance_id=instance.get(
                        "InstanceId"
                    ),
                    instance_type=instance.get(
                        "InstanceType"
                    ),
                    state=instance.get(
                        "State",
                        {}
                    ).get("Name"),
                    private_ip=instance.get(
                        "PrivateIpAddress"
                    ),
                    public_ip=instance.get(
                        "PublicIpAddress"
                    ),
                )
            )

    return instances


@mcp.tool()
def get_ec2_instance_status(
    instance_id: str,
) -> EC2InstanceStatus:
    """Get the current status of a specific EC2 instance."""

    ec2 = get_ec2_client()

    try:

        response = ec2.describe_instance_status(
            InstanceIds=[instance_id],
            IncludeAllInstances=True,
        )

    except ClientError as exc:

        error_code = exc.response.get(
            "Error",
            {}
        ).get("Code")

        if error_code in [
            "InvalidInstanceID.NotFound",
            "InvalidInstanceID.Malformed",
        ]:

            return EC2InstanceStatus(
                instance_id=instance_id,
                found=False,
                message=(
                    "EC2 instance was not found or "
                    "the instance ID is invalid."
                ),
            )

        raise

    statuses = response.get(
        "InstanceStatuses",
        []
    )

    if not statuses:

        return EC2InstanceStatus(
            instance_id=instance_id,
            found=False,
            message=(
                "No EC2 status information found."
            ),
        )

    status = statuses[0]

    return EC2InstanceStatus(
        instance_id=instance_id,
        found=True,
        instance_state=status.get(
            "InstanceState",
            {}
        ).get("Name"),
        system_status=status.get(
            "SystemStatus",
            {}
        ).get("Status"),
        instance_status=status.get(
            "InstanceStatus",
            {}
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

    for alarm in response.get(
        "MetricAlarms",
        []
    ):

        alarms.append(
            CloudWatchAlarm(
                alarm_name=alarm.get(
                    "AlarmName"
                ),
                state=alarm.get(
                    "StateValue"
                ),
                state_reason=alarm.get(
                    "StateReason"
                ),
                metric_name=alarm.get(
                    "MetricName"
                ),
                namespace=alarm.get(
                    "Namespace"
                ),
                dimensions=alarm.get(
                    "Dimensions",
                    []
                ),
            )
        )

    return alarms


# ============================================================
# CONTROLLED REMEDIATION
# ============================================================

@mcp.tool()
def reboot_ec2_instance(
    instance_id: str,
    approved: bool,
    dry_run: bool = True,
) -> EC2RebootResult:
    """
    Controlled EC2 reboot operation.

    Safety rules:

    1. Explicit approval is required.
    2. Dry-run is the default.
    3. Actual execution requires:
           approved=True
           dry_run=False
    4. Only one narrowly scoped operation is exposed.
    """

    # --------------------------------------------------------
    # Validate instance ID format
    # --------------------------------------------------------

    if not re.fullmatch(
        r"i-[0-9a-fA-F]+",
        instance_id,
    ):

        return EC2RebootResult(
            instance_id=instance_id,
            approved=approved,
            dry_run=dry_run,
            executed=False,
            success=False,
            message=(
                "Invalid EC2 instance ID format."
            ),
        )

    # --------------------------------------------------------
    # Approval guard
    # --------------------------------------------------------

    if not approved:

        return EC2RebootResult(
            instance_id=instance_id,
            approved=False,
            dry_run=dry_run,
            executed=False,
            success=False,
            message=(
                "Execution blocked because explicit "
                "human approval was not provided."
            ),
        )

    ec2 = get_ec2_client()

    # --------------------------------------------------------
    # DRY RUN
    # --------------------------------------------------------

    if dry_run:

        try:

            ec2.reboot_instances(
                InstanceIds=[instance_id],
                DryRun=True,
            )

            return EC2RebootResult(
                instance_id=instance_id,
                approved=True,
                dry_run=True,
                executed=False,
                success=False,
                message=(
                    "Dry-run request returned without "
                    "the expected DryRunOperation response."
                ),
            )

        except ClientError as exc:

            error_code = exc.response.get(
                "Error",
                {}
            ).get("Code")

            if error_code == "DryRunOperation":

                return EC2RebootResult(
                    instance_id=instance_id,
                    approved=True,
                    dry_run=True,
                    executed=False,
                    success=True,
                    message=(
                        "Dry-run validation succeeded. "
                        "No reboot was performed."
                    ),
                )

            if error_code in [
                "InvalidInstanceID.NotFound",
                "InvalidInstanceID.Malformed",
            ]:

                return EC2RebootResult(
                    instance_id=instance_id,
                    approved=True,
                    dry_run=True,
                    executed=False,
                    success=False,
                    message=(
                        "EC2 instance was not found "
                        "or the instance ID is invalid."
                    ),
                )

            raise

    # --------------------------------------------------------
    # ACTUAL CONTROLLED EXECUTION
    # --------------------------------------------------------

    try:

        ec2.reboot_instances(
            InstanceIds=[instance_id],
            DryRun=False,
        )

    except ClientError as exc:

        error_code = exc.response.get(
            "Error",
            {}
        ).get("Code")

        if error_code in [
            "InvalidInstanceID.NotFound",
            "InvalidInstanceID.Malformed",
        ]:

            return EC2RebootResult(
                instance_id=instance_id,
                approved=True,
                dry_run=False,
                executed=False,
                success=False,
                message=(
                    "EC2 instance was not found "
                    "or the instance ID is invalid."
                ),
            )

        raise

    return EC2RebootResult(
        instance_id=instance_id,
        approved=True,
        dry_run=False,
        executed=True,
        success=True,
        message=(
            "EC2 reboot request submitted successfully."
        ),
    )


# ============================================================
# SERVER ENTRY POINT
# ============================================================

if __name__ == "__main__":
    mcp.run()