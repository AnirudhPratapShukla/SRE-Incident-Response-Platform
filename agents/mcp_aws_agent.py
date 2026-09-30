import asyncio

from graph.state import IncidentState
from mcp_client.aws_client import (
    list_ec2_instances,
    get_cloudwatch_alarms,
)


def mcp_aws_agent(
    state: IncidentState,
) -> IncidentState:
    """
    Collect read-only AWS infrastructure context through MCP.

    This agent does not modify AWS resources.
    """

    print(
        "\n[MCP AWS Agent] "
        "Collecting AWS context through MCP..."
    )

    async def collect_context():

        ec2_instances = await list_ec2_instances()

        cloudwatch_alarms = await get_cloudwatch_alarms()

        return (
            ec2_instances,
            cloudwatch_alarms,
        )

    (
        ec2_instances,
        cloudwatch_alarms,
    ) = asyncio.run(
        collect_context()
    )

    state["mcp_ec2_instances"] = (
        ec2_instances.get("result", [])
        if ec2_instances
        else []
    )

    state["mcp_cloudwatch_alarms"] = (
        cloudwatch_alarms.get("result", [])
        if cloudwatch_alarms
        else []
    )

    print(
        "[MCP AWS Agent] "
        f"EC2 instances collected: "
        f"{len(state['mcp_ec2_instances'])}"
    )

    print(
        "[MCP AWS Agent] "
        f"CloudWatch alarms collected: "
        f"{len(state['mcp_cloudwatch_alarms'])}"
    )

    return state