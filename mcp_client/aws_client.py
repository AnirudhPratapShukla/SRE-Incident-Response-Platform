from mcp import Client

from mcp_servers import aws_server


async def list_ec2_instances():
    """
    Retrieve EC2 instances through the AWS MCP server.
    """

    async with Client(aws_server.mcp) as client:

        result = await client.call_tool(
            "list_ec2_instances",
            {},
        )

        if result.is_error:
            raise RuntimeError(
                "MCP EC2 list tool failed."
            )

        return result.structured_content


async def get_ec2_instance_status(
    instance_id: str,
):
    """
    Retrieve EC2 instance status through the AWS MCP server.
    """

    async with Client(aws_server.mcp) as client:

        result = await client.call_tool(
            "get_ec2_instance_status",
            {
                "instance_id": instance_id,
            },
        )

        if result.is_error:
            raise RuntimeError(
                "MCP EC2 status tool failed."
            )

        return result.structured_content


async def get_cloudwatch_alarms():
    """
    Retrieve CloudWatch ALARM state through the AWS MCP server.
    """

    async with Client(aws_server.mcp) as client:

        result = await client.call_tool(
            "get_cloudwatch_alarms",
            {},
        )

        if result.is_error:
            raise RuntimeError(
                "MCP CloudWatch alarm tool failed."
            )

        return result.structured_content