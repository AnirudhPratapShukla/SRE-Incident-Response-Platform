import asyncio

from mcp_client.aws_client import (
    list_ec2_instances,
    get_ec2_instance_status,
    get_cloudwatch_alarms,
    reboot_ec2_instance,
)

from mcp_servers import aws_server

from botocore.exceptions import ClientError


TEST_INSTANCE_ID = "i-123abc456def"


class FakeEC2Client:

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


def test_client_list_ec2_instances():

    async def run():

        result = await list_ec2_instances()

        assert result is not None
        assert "result" in result
        assert isinstance(result["result"], list)

    asyncio.run(run())


def test_client_get_ec2_instance_status():

    async def run():

        # Valid EC2 instance ID format,
        # but expected not to exist in the test account.
        result = await get_ec2_instance_status(
            "i-00000000000000000"
        )

        assert result is not None
        assert result["instance_id"] == "i-00000000000000000"
        assert result["found"] is False

    asyncio.run(run())


def test_client_get_cloudwatch_alarms():

    async def run():

        result = await get_cloudwatch_alarms()

        assert result is not None
        assert "result" in result
        assert isinstance(result["result"], list)

    asyncio.run(run())


def test_client_reboot_blocked_without_approval():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        result = await reboot_ec2_instance(
            TEST_INSTANCE_ID,
            approved=False,
            dry_run=False,
        )

        assert result is not None
        assert result["instance_id"] == TEST_INSTANCE_ID
        assert result["approved"] is False
        assert result["dry_run"] is False
        assert result["executed"] is False
        assert result["success"] is False
        assert "approval" in result["message"].lower()

    asyncio.run(run())


def test_client_reboot_dry_run():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        result = await reboot_ec2_instance(
            TEST_INSTANCE_ID,
            approved=True,
            dry_run=True,
        )

        assert result is not None
        assert result["instance_id"] == TEST_INSTANCE_ID
        assert result["approved"] is True
        assert result["dry_run"] is True
        assert result["executed"] is False
        assert result["success"] is True
        assert "dry-run" in result["message"].lower()

    asyncio.run(run())


def test_client_reboot_actual_execution():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        result = await reboot_ec2_instance(
            TEST_INSTANCE_ID,
            approved=True,
            dry_run=False,
        )

        assert result is not None
        assert result["instance_id"] == TEST_INSTANCE_ID
        assert result["approved"] is True
        assert result["dry_run"] is False
        assert result["executed"] is True
        assert result["success"] is True
        assert "reboot" in result["message"].lower()

    asyncio.run(run())