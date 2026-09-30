import asyncio

from mcp_client.aws_client import (
    list_ec2_instances,
    get_ec2_instance_status,
    get_cloudwatch_alarms,
)


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