import asyncio

from mcp import Client

from mcp_servers import aws_server


class FakeEC2Client:

    def describe_instances(self):
        return {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-test123",
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

            assert data["result"][0]["instance_id"] == "i-test123"
            assert data["result"][0]["state"] == "running"

    asyncio.run(run())


def test_get_ec2_instance_status():

    aws_server.get_ec2_client = lambda: FakeEC2Client()

    async def run():

        async with Client(aws_server.mcp) as client:

            result = await client.call_tool(
                "get_ec2_instance_status",
                {
                    "instance_id": "i-test123",
                },
            )

            assert result.is_error is False
            assert result.structured_content is not None

            data = result.structured_content

            assert data["instance_id"] == "i-test123"
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