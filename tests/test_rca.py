from agents.rca_agent import (
    parse_rca_response,
    build_rca_prompt,
)


def test_rca_parser():

    sample_response = """
MOST LIKELY ROOT CAUSE:
Database connection pool exhaustion.

SUPPORTING EVIDENCE:
Database connection timeouts and connection pool
exhaustion warnings are present in the logs.

IMPACT:
Requests are timing out and HTTP 500 errors are
being returned by the order-api service.

RECOMMENDED FIX:
Increase the database connection pool size and
optimize database connection handling.

ROLLBACK PLAN:
Restore the previous database connection pool
configuration if unexpected behavior occurs.

PREVENTION RECOMMENDATIONS:
Perform load testing and monitor database
connection pool utilization.
"""

    result = parse_rca_response(
        sample_response
    )

    assert (
        result["root_cause"]
        == "Database connection pool exhaustion."
    )

    assert "connection timeouts" in (
        result["supporting_evidence"]
    )

    assert "HTTP 500" in (
        result["impact"]
    )

    assert "Increase the database connection pool" in (
        result["recommendation"]
    )

    assert "Restore the previous database connection" in (
        result["rollback_plan"]
    )


def test_rca_prompt_contains_mcp_ec2_context():

    state = {
        "service": "order-api",
        "metrics": "CPU utilization is high.",
        "logs": "Application timeout detected.",
        "infrastructure": "Infrastructure appears healthy.",
        "historical_incidents": "No similar incidents found.",
        "mcp_ec2_instances": [
            {
                "instance_id": "i-test123",
                "instance_type": "t3.micro",
                "state": "running",
            }
        ],
        "mcp_cloudwatch_alarms": [],
    }

    prompt = build_rca_prompt(
        state
    )

    assert "LIVE AWS CONTEXT FROM MCP" in prompt
    assert "EC2 INSTANCES" in prompt
    assert "i-test123" in prompt
    assert "t3.micro" in prompt
    assert "running" in prompt


def test_rca_prompt_contains_mcp_cloudwatch_context():

    state = {
        "service": "order-api",
        "metrics": "CPU utilization is high.",
        "logs": "Application timeout detected.",
        "infrastructure": "Infrastructure appears healthy.",
        "historical_incidents": "No similar incidents found.",
        "mcp_ec2_instances": [],
        "mcp_cloudwatch_alarms": [
            {
                "alarm_name": "TestHighCPU",
                "state": "ALARM",
                "metric_name": "CPUUtilization",
                "namespace": "AWS/EC2",
            }
        ],
    }

    prompt = build_rca_prompt(
        state
    )

    assert "LIVE AWS CONTEXT FROM MCP" in prompt
    assert "CLOUDWATCH ALARMS CURRENTLY IN ALARM STATE" in prompt
    assert "TestHighCPU" in prompt
    assert "CPUUtilization" in prompt
    assert "ALARM" in prompt


def test_rca_prompt_handles_empty_mcp_context():

    state = {
        "service": "order-api",
        "metrics": "No metrics available.",
        "logs": "No logs available.",
        "infrastructure": "No infrastructure information available.",
        "historical_incidents": "No historical incidents available.",
        "mcp_ec2_instances": [],
        "mcp_cloudwatch_alarms": [],
    }

    prompt = build_rca_prompt(
        state
    )

    assert "LIVE AWS CONTEXT FROM MCP" in prompt
    assert "EC2 INSTANCES" in prompt
    assert "CLOUDWATCH ALARMS CURRENTLY IN ALARM STATE" in prompt

    assert (
        "Do not assume that an empty MCP result means an error."
        in prompt
    )

    assert (
        "An empty list means that no matching resources were"
        in prompt
    )