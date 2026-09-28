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

    assert client.base_url == "https://example.atlassian.net"
    assert client.email == "test@example.com"


def test_jira_client_requires_base_url(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "")
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
        "historical_incidents": "Similar incident found",
        "root_cause": "Database connection saturation",
        "supporting_evidence": "Connection pool exhausted",
        "impact": "Order requests failing",
        "recommendation": "Increase database connection capacity",
        "rollback_plan": "Restore previous configuration",
        "risk_level": "MEDIUM",
        "safety_status": "APPROVED",
    }

    fields = build_incident_fields(state)

    assert fields["project"]["key"] == "SRE"
    assert fields["issuetype"]["id"] == "10010"
    assert fields["summary"] == (
        "[Incident] order-api: HTTP 500 errors"
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
            "project": {"key": "SRE"},
            "issuetype": {"id": "10010"},
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
    assert result["name"] == "SRE Incident Response"