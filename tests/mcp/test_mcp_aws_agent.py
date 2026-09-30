import asyncio

from agents import mcp_aws_agent as module


def test_mcp_aws_agent_collects_context(monkeypatch):

    async def fake_list_ec2_instances():

        return {
            "result": [
                {
                    "instance_id": "i-test123",
                    "instance_type": "t3.micro",
                    "state": "running",
                }
            ]
        }

    async def fake_get_cloudwatch_alarms():

        return {
            "result": [
                {
                    "alarm_name": "TestHighCPU",
                    "state": "ALARM",
                    "metric_name": "CPUUtilization",
                }
            ]
        }

    monkeypatch.setattr(
        module,
        "list_ec2_instances",
        fake_list_ec2_instances,
    )

    monkeypatch.setattr(
        module,
        "get_cloudwatch_alarms",
        fake_get_cloudwatch_alarms,
    )

    state = {
        "incident": "High CPU",
        "service": "EC2",
    }

    result = module.mcp_aws_agent(state)

    assert result["mcp_ec2_instances"] == [
        {
            "instance_id": "i-test123",
            "instance_type": "t3.micro",
            "state": "running",
        }
    ]

    assert result["mcp_cloudwatch_alarms"] == [
        {
            "alarm_name": "TestHighCPU",
            "state": "ALARM",
            "metric_name": "CPUUtilization",
        }
    ]


def test_mcp_aws_agent_handles_empty_results(monkeypatch):

    async def fake_list_ec2_instances():

        return {
            "result": []
        }

    async def fake_get_cloudwatch_alarms():

        return {
            "result": []
        }

    monkeypatch.setattr(
        module,
        "list_ec2_instances",
        fake_list_ec2_instances,
    )

    monkeypatch.setattr(
        module,
        "get_cloudwatch_alarms",
        fake_get_cloudwatch_alarms,
    )

    state = {
        "incident": "Test incident",
        "service": "AWS",
    }

    result = module.mcp_aws_agent(state)

    assert result["mcp_ec2_instances"] == []
    assert result["mcp_cloudwatch_alarms"] == []