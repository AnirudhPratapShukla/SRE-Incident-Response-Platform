from unittest.mock import Mock

import pytest

from jira.client import JiraClient, JiraClientError
from jira.incidents import build_incident_fields


def test_jira_client_configuration(monkeypatch):
    monkeypatch.setenv(
        "JIRA_BASE_URL",
        "https://example.atlassian.net",
    )

    monkeypatch.setenv(
        "JIRA_EMAIL",
        "test@example.com",
    )

    monkeypatch.setenv(
        "JIRA_API_TOKEN",
        "fake-token",
    )

    client = JiraClient()

    assert (
        client.base_url
        == "https://example.atlassian.net"
    )

    assert (
        client.email
        == "test@example.com"
    )


def test_jira_client_requires_base_url(monkeypatch):
    monkeypatch.setenv(
        "JIRA_BASE_URL",
        "",
    )

    monkeypatch.setenv(
        "JIRA_EMAIL",
        "test@example.com",
    )

    monkeypatch.setenv(
        "JIRA_API_TOKEN",
        "fake-token",
    )

    with pytest.raises(JiraClientError):
        JiraClient()


def test_build_incident_fields(monkeypatch):
    monkeypatch.setenv(
        "JIRA_PROJECT_KEY",
        "SRE",
    )

    monkeypatch.setenv(
        "JIRA_INCIDENT_ISSUE_TYPE_ID",
        "10010",
    )

    state = {
        "incident": "HTTP 500 errors",
        "service": "order-api",
        "incident_source": "AWS CloudWatch",
        "aws_region": "us-east-1",
        "cloudwatch_alarm_name": "OrderApiErrors",
        "cloudwatch_alarm_state": "ALARM",
        "cloudwatch_metric": "HTTP5XX",
        "metrics": "High error rate",
        "logs": "HTTP 500 responses detected",
        "infrastructure": "order-api infrastructure",
        "historical_incidents": (
            "Similar incident found"
        ),
        "root_cause": (
            "Database connection saturation"
        ),
        "supporting_evidence": (
            "Connection pool exhausted"
        ),
        "impact": "Order requests failing",
        "recommendation": (
            "Increase database connection capacity"
        ),
        "rollback_plan": (
            "Restore previous configuration"
        ),
        "risk_level": "MEDIUM",
        "safety_status": "APPROVED",
    }

    fields = build_incident_fields(state)

    assert fields["project"]["key"] == "SRE"
    assert fields["issuetype"]["id"] == "10010"

    assert (
        fields["summary"]
        == "[Incident] order-api: HTTP 500 errors"
    )

    assert fields["description"]["type"] == "doc"
    assert fields["description"]["version"] == 1


def test_create_issue_request():
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
    )

    response = Mock()
    response.ok = True

    response.json.return_value = {
        "id": "10001",
        "key": "SRE-1",
    }

    client.session.request = Mock(
        return_value=response
    )

    result = client.create_issue(
        {
            "project": {
                "key": "SRE",
            },
            "issuetype": {
                "id": "10010",
            },
            "summary": "Test incident",
        }
    )

    assert result["key"] == "SRE-1"

    client.session.request.assert_called_once()


def test_get_project():
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
    )

    response = Mock()
    response.ok = True

    response.json.return_value = {
        "key": "SRE",
        "name": "SRE Incident Response",
    }

    client.session.request = Mock(
        return_value=response
    )

    result = client.get_project("SRE")

    assert result["key"] == "SRE"

    assert (
        result["name"]
        == "SRE Incident Response"
    )


def test_get_transitions():
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
    )

    response = Mock()
    response.ok = True

    response.json.return_value = {
        "transitions": [
            {
                "id": "11",
                "name": "To Do",
                "to": {
                    "name": "To Do",
                },
            },
            {
                "id": "21",
                "name": "In Progress",
                "to": {
                    "name": "In Progress",
                },
            },
            {
                "id": "31",
                "name": "In Review",
                "to": {
                    "name": "In Review",
                },
            },
            {
                "id": "41",
                "name": "Done",
                "to": {
                    "name": "Done",
                },
            },
        ]
    }

    client.session.request = Mock(
        return_value=response
    )

    transitions = client.get_transitions("SRE-4")

    assert len(transitions) == 4

    assert transitions[1]["id"] == "21"

    assert (
        transitions[1]["to"]["name"]
        == "In Progress"
    )


def test_transition_issue():
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
    )

    response = Mock()
    response.ok = True
    response.json.return_value = {}

    client.session.request = Mock(
        return_value=response
    )

    result = client.transition_issue(
        "SRE-4",
        "21",
    )

    assert result is None

    client.session.request.assert_called_once()

    call = client.session.request.call_args

    assert call.args[0] == "POST"

    assert (
        call.args[1]
        == "https://example.atlassian.net/"
        "rest/api/3/issue/SRE-4/transitions"
    )

    assert (
        call.kwargs["json"]
        == {
            "transition": {
                "id": "21",
            }
        }
    )

def test_transition_issue_to_status():
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
    )

    transitions_response = Mock()
    transitions_response.ok = True

    transitions_response.json.return_value = {
        "transitions": [
            {
                "id": "11",
                "name": "To Do",
                "to": {
                    "name": "To Do",
                },
            },
            {
                "id": "21",
                "name": "In Progress",
                "to": {
                    "name": "In Progress",
                },
            },
            {
                "id": "31",
                "name": "In Review",
                "to": {
                    "name": "In Review",
                },
            },
            {
                "id": "41",
                "name": "Done",
                "to": {
                    "name": "Done",
                },
            },
        ]
    }

    transition_response = Mock()
    transition_response.ok = True
    transition_response.json.return_value = {}

    client.session.request = Mock(
        side_effect=[
            transitions_response,
            transition_response,
        ]
    )

    result = client.transition_issue_to_status(
        "SRE-4",
        "In Progress",
    )

    assert result is None

    assert (
        client.session.request.call_count
        == 2
    )

    first_call = (
        client.session.request.call_args_list[0]
    )

    assert first_call.args[0] == "GET"

    assert (
        first_call.args[1]
        == "https://example.atlassian.net/"
        "rest/api/3/issue/SRE-4/transitions"
    )

    second_call = (
        client.session.request.call_args_list[1]
    )

    assert second_call.args[0] == "POST"

    assert (
        second_call.args[1]
        == "https://example.atlassian.net/"
        "rest/api/3/issue/SRE-4/transitions"
    )

    assert (
        second_call.kwargs["json"]
        == {
            "transition": {
                "id": "21",
            }
        }
    )


def test_transition_issue_to_status_not_found():
    client = JiraClient(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="fake-token",
    )

    response = Mock()
    response.ok = True

    response.json.return_value = {
        "transitions": [
            {
                "id": "21",
                "name": "In Progress",
                "to": {
                    "name": "In Progress",
                },
            }
        ]
    }

    client.session.request = Mock(
        return_value=response
    )

    with pytest.raises(JiraClientError) as exc_info:
        client.transition_issue_to_status(
            "SRE-4",
            "Done",
        )

    assert (
        "No Jira transition found"
        in str(exc_info.value)
    )

    assert (
        "Done"
        in str(exc_info.value)
    )

def test_transition_incident_to_status():
    from jira.incidents import (
        transition_incident_to_status,
    )

    fake_client = Mock()

    transition_incident_to_status(
        issue_key="SRE-4",
        status_name="In Progress",
        client=fake_client,
    )

    fake_client.transition_issue_to_status.assert_called_once_with(
        issue_key="SRE-4",
        status_name="In Progress",
    )


def test_create_incident_uses_client():
    from jira.incidents import create_incident

    fake_client = Mock()

    fake_client.create_issue.return_value = {
        "id": "10013",
        "key": "SRE-4",
    }

    state = {
        "incident": "HTTP 500 errors",
        "service": "order-api",
    }

    result = create_incident(
        state,
        client=fake_client,
    )

    assert result["key"] == "SRE-4"

    fake_client.create_issue.assert_called_once()

def test_mark_in_progress():
    from jira.lifecycle import mark_in_progress

    fake_client = Mock()

    mark_in_progress(
        "SRE-4",
        client=fake_client,
    )

    fake_client.transition_issue_to_status.assert_called_once_with(
        issue_key="SRE-4",
        status_name="In Progress",
    )


def test_mark_in_review():
    from jira.lifecycle import mark_in_review

    fake_client = Mock()

    mark_in_review(
        "SRE-4",
        client=fake_client,
    )

    fake_client.transition_issue_to_status.assert_called_once_with(
        issue_key="SRE-4",
        status_name="In Review",
    )


def test_mark_done():
    from jira.lifecycle import mark_done

    fake_client = Mock()

    mark_done(
        "SRE-4",
        client=fake_client,
    )

    fake_client.transition_issue_to_status.assert_called_once_with(
        issue_key="SRE-4",
        status_name="Done",
    )