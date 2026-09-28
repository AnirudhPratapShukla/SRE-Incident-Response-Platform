from unittest.mock import patch

from services.cloudwatch_incident_runner import (
    start_cloudwatch_incidents,
)


class FakeGraph:

    def __init__(self):
        self.updated_states = []
        self.invocations = []

    def update_state(self, config, state):
        self.updated_states.append(
            {
                "config": config,
                "state": state,
            }
        )

    def invoke(self, command, config):
        self.invocations.append(
            {
                "command": command,
                "config": config,
            }
        )

        return {
            "status": "started"
        }


def sample_incident():

    return {
        "incident": (
            "CloudWatch alarm 'HighCPU-order-api' "
            "is in ALARM state."
        ),
        "service": "i-0123456789abcdef0",
        "incident_source": "AWS CloudWatch",
        "aws_region": "us-east-1",
        "cloudwatch_alarm_name": (
            "HighCPU-order-api"
        ),
        "cloudwatch_alarm_state": "ALARM",
        "cloudwatch_metric": (
            "AWS/EC2/CPUUtilization"
        ),
    }


@patch(
    "services.cloudwatch_incident_runner.incident_graph"
)
@patch(
    "services.cloudwatch_incident_runner.detect_cloudwatch_incidents"
)
def test_start_cloudwatch_incidents(
    mock_detect,
    mock_graph,
):

    fake_graph = FakeGraph()

    mock_graph.update_state = (
        fake_graph.update_state
    )

    mock_graph.invoke = (
        fake_graph.invoke
    )

    mock_detect.return_value = [
        sample_incident()
    ]

    results = start_cloudwatch_incidents(
        region_name="us-east-1"
    )

    assert len(results) == 1

    result = results[0]

    assert "thread_id" in result

    assert result["thread_id"]

    assert result["incident"] == (
        sample_incident()
    )

    assert result["result"] == {
        "status": "started"
    }

    assert len(fake_graph.updated_states) == 1

    updated_state = (
        fake_graph.updated_states[0]
    )

    assert updated_state["state"] == (
        sample_incident()
    )

    assert (
        updated_state["config"]["configurable"][
            "thread_id"
        ]
        == result["thread_id"]
    )

    assert len(fake_graph.invocations) == 1

    invocation = fake_graph.invocations[0]

    assert invocation["command"] is None

    assert (
        invocation["config"]["configurable"][
            "thread_id"
        ]
        == result["thread_id"]
    )


@patch(
    "services.cloudwatch_incident_runner.incident_graph"
)
@patch(
    "services.cloudwatch_incident_runner.detect_cloudwatch_incidents"
)
def test_start_cloudwatch_incidents_when_empty(
    mock_detect,
    mock_graph,
):

    mock_detect.return_value = []

    results = start_cloudwatch_incidents(
        region_name="us-east-1"
    )

    assert results == []

    mock_graph.update_state.assert_not_called()

    mock_graph.invoke.assert_not_called()
