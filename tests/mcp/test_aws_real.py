import asyncio

from mcp import Client

from mcp_servers import aws_server


async def main():

    async with Client(aws_server.mcp) as client:

        print("\n=== MCP AWS REAL SMOKE TEST ===")

        print("\n[1] EC2 Instances")

        result = await client.call_tool(
            "list_ec2_instances",
            {},
        )

        if result.is_error:
            print("EC2 tool failed:")
            print(result)
            return

        print(result.structured_content)

        print("\n[2] CloudWatch ALARM State")

        result = await client.call_tool(
            "get_cloudwatch_alarms",
            {},
        )

        if result.is_error:
            print("CloudWatch tool failed:")
            print(result)
            return

        print(result.structured_content)

        print("\n=== SMOKE TEST SUCCESS ===")


if __name__ == "__main__":
    asyncio.run(main())