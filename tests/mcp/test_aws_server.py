import asyncio

from botocore.exceptions import ClientError
from mcp import Client

from mcp_servers import aws_server


TEST_INSTANCE_ID = "i-123abc456def"


class FakeEC2Client:

    def describe_instances(self):
        return {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": TEST_INSTANCE_ID,
                            "InstanceType": "t3.micro",
                            "State": {"Name": "running"},
                            "PrivateIpAddress": "10.0.0.10",
                            "PublicIpAddress": "54.1.2.3",
                        }
                    ]
                }
            ]
        }

    def describe_instance_status(
        self,
        InstanceIds,
        IncludeAllInstances,
    ):
        return {
            "InstanceStatuses": [
                {
                    "InstanceId": InstanceIds[0],
                    "InstanceState": {"Name": "running"},
                    "SystemStatus": {"Status": "ok"},
                    "InstanceStatus": {"Status": "ok"},
                }
            ]
        }

    def reboot_instances(
        self,
        InstanceIds,
        DryRun,
    ):
        if DryRun:
            raise ClientError(
                {
                    "Error": {
                        "Code": "DryRunOperation",
                        "Message": (
                            "Request would have succeeded, "
                            "but DryRun flag is set."
                        ),
                    }
                },
                "RebootInstances",
            )

        return {}


class FakeCloudWatchClient:

    def describe_alarms(self, StateValue):
        return {
            "MetricAlarms": [
                {
                    "AlarmName": "TestHighCPU",
                    "StateValue": "ALARM",
                    "StateReason": "Test alarm",
                    "MetricName": "CPUUtilization",
                    "Namespace": "AWS/EC2",
                    "Dimensions": [],
                }
            ]
        }


def test_mcp_tools_registered():

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.list_tools()

            tool_names = [
                tool.name
                for tool in result.tools
            ]

            assert "list_ec2_instances" in tool_names
            assert "get_ec2_instance_status" in tool_names
            assert "get_cloudwatch_alarms" in tool_names
            assert "reboot_ec2_instance" in tool_names

    asyncio.run(run())


def test_list_ec2_instances():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.call_tool(
                "list_ec2_instances",
                {},
            )

            assert result.is_error is False
            assert result.structured_content is not None

            data = result.structured_content

            assert data["result"][0]["instance_id"] == TEST_INSTANCE_ID
            assert data["result"][0]["state"] == "running"

    asyncio.run(run())


def test_get_ec2_instance_status():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.call_tool(
                "get_ec2_instance_status",
                {
                    "instance_id": TEST_INSTANCE_ID,
                },
            )

            assert result.is_error is False
            assert result.structured_content is not None

            data = result.structured_content

            assert data["instance_id"] == TEST_INSTANCE_ID
            assert data["found"] is True
            assert data["instance_state"] == "running"
            assert data["system_status"] == "ok"
            assert data["instance_status"] == "ok"

    asyncio.run(run())


def test_get_cloudwatch_alarms():

    aws_server.get_cloudwatch_client = (
        lambda: FakeCloudWatchClient()
    )

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.call_tool(
                "get_cloudwatch_alarms",
                {},
            )

            assert result.is_error is False
            assert result.structured_content is not None

            data = result.structured_content

            assert data["result"][0]["alarm_name"] == "TestHighCPU"
            assert data["result"][0]["state"] == "ALARM"

    asyncio.run(run())


def test_reboot_ec2_instance_blocked_without_approval():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.call_tool(
                "reboot_ec2_instance",
                {
                    "instance_id": TEST_INSTANCE_ID,
                    "approved": False,
                    "dry_run": False,
                },
            )

            assert result.is_error is False
            assert result.structured_content is not None

            data = result.structured_content

            assert data["instance_id"] == TEST_INSTANCE_ID
            assert data["approved"] is False
            assert data["dry_run"] is False
            assert data["executed"] is False
            assert data["success"] is False
            assert "approval" in data["message"].lower()

    asyncio.run(run())


def test_reboot_ec2_instance_dry_run():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.call_tool(
                "reboot_ec2_instance",
                {
                    "instance_id": TEST_INSTANCE_ID,
                    "approved": True,
                    "dry_run": True,
                },
            )

            assert result.is_error is False
            assert result.structured_content is not None

            data = result.structured_content

            assert data["instance_id"] == TEST_INSTANCE_ID
            assert data["approved"] is True
            assert data["dry_run"] is True
            assert data["executed"] is False
            assert data["success"] is True
            assert "dry-run" in data["message"].lower()

    asyncio.run(run())


def test_reboot_ec2_instance_actual_execution():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.call_tool(
                "reboot_ec2_instance",
                {
                    "instance_id": TEST_INSTANCE_ID,
                    "approved": True,
                    "dry_run": False,
                },
            )

            assert result.is_error is False
            assert result.structured_content is not None

            data = result.structured_content

            assert data["instance_id"] == TEST_INSTANCE_ID
            assert data["approved"] is True
            assert data["dry_run"] is False
            assert data["executed"] is True
            assert data["success"] is True
            assert "reboot" in data["message"].lower()

    asyncio.run(run())


def test_reboot_ec2_instance_invalid_instance_id():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.call_tool(
                "reboot_ec2_instance",
                {
                    "instance_id": "invalid-instance-id",
                    "approved": True,
                    "dry_run": True,
                },
            )

            assert result.is_error is False
            assert result.structured_content is not None

            data = result.structured_content

            assert data["approved"] is True
            assert data["dry_run"] is True
            assert data["executed"] is False
            assert data["success"] is False
            assert "invalid" in data["message"].lower()

    asyncio.run(run())