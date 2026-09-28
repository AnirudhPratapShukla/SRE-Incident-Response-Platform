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
    "services.cloudwatch_incident_runner.create_incident"
)
@patch(
    "services.cloudwatch_incident_runner.incident_graph"
)
@patch(
    "services.cloudwatch_incident_runner.detect_cloudwatch_incidents"
)
def test_start_cloudwatch_incidents(
    mock_detect,
    mock_graph,
    mock_create_incident,
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

    mock_create_incident.return_value = {
        "id": "10013",
        "key": "SRE-4",
        "self": (
            "https://shuklaanirudhpratap.atlassian.net/"
            "rest/api/3/issue/10013"
        ),
    }

    results = start_cloudwatch_incidents(
        region_name="us-east-1"
    )

    assert len(results) == 1

    result = results[0]

    assert "thread_id" in result
    assert result["thread_id"]

    assert result["incident"]["incident"] == (
        sample_incident()["incident"]
    )

    assert result["incident"]["jira_issue_key"] == (
        "SRE-4"
    )

    assert result["incident"]["jira_status"] == (
        "CREATED"
    )

    assert result["incident"]["jira_issue_url"] == (
        "https://shuklaanirudhpratap.atlassian.net/"
        "browse/SRE-4"
    )

    assert result["jira"] == {
        "id": "10013",
        "key": "SRE-4",
        "self": (
            "https://shuklaanirudhpratap.atlassian.net/"
            "rest/api/3/issue/10013"
        ),
    }

    assert result["result"] == {
        "status": "started"
    }

    mock_create_incident.assert_called_once()

    jira_argument = (
        mock_create_incident.call_args.args[0]
    )

    assert jira_argument["jira_issue_key"] == (
        "SRE-4"
    )

    assert len(fake_graph.updated_states) == 1

    updated_state = (
        fake_graph.updated_states[0]
    )

    assert updated_state["state"]["jira_issue_key"] == (
        "SRE-4"
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
    "services.cloudwatch_incident_runner.create_incident"
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
    mock_create_incident,
):

    mock_detect.return_value = []

    results = start_cloudwatch_incidents(
        region_name="us-east-1"
    )

    assert results == []

    mock_create_incident.assert_not_called()

    mock_graph.update_state.assert_not_called()

    mock_graph.invoke.assert_not_called()


@patch(
    "services.cloudwatch_incident_runner.create_incident"
)
@patch(
    "services.cloudwatch_incident_runner.incident_graph"
)
@patch(
    "services.cloudwatch_incident_runner.detect_cloudwatch_incidents"
)
def test_start_cloudwatch_incidents_stops_when_jira_fails(
    mock_detect,
    mock_graph,
    mock_create_incident,
):

    mock_detect.return_value = [
        sample_incident()
    ]

    mock_create_incident.side_effect = RuntimeError(
        "Jira unavailable"
    )

    try:
        start_cloudwatch_incidents(
            region_name="us-east-1"
        )
        assert False, (
            "Expected Jira failure to stop "
            "CloudWatch incident processing."
        )
    except RuntimeError as exc:
        assert str(exc) == "Jira unavailable"

    mock_graph.update_state.assert_not_called()
    mock_graph.invoke.assert_not_called()