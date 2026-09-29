import os
from typing import Any

from dotenv import load_dotenv

from graph.state import IncidentState
from jira.client import JiraClient


def _text(
    value: Any,
    default: str = "Not available",
) -> str:
    """Convert a value to clean text."""

    if value is None:
        return default

    value = str(value).strip()

    return value if value else default


def _paragraph(
    text: str,
) -> dict[str, Any]:
    """Create a Jira ADF paragraph."""

    return {
        "type": "paragraph",
        "content": [
            {
                "type": "text",
                "text": text,
            }
        ],
    }


def build_incident_fields(
    state: IncidentState,
) -> dict[str, Any]:
    """Build Jira fields from an IncidentState."""

    load_dotenv()

    project_key = os.getenv(
        "JIRA_PROJECT_KEY"
    )

    issue_type_id = os.getenv(
        "JIRA_INCIDENT_ISSUE_TYPE_ID"
    )

    if not project_key:
        raise ValueError(
            "JIRA_PROJECT_KEY is not configured."
        )

    if not issue_type_id:
        raise ValueError(
            "JIRA_INCIDENT_ISSUE_TYPE_ID "
            "is not configured."
        )

    service = _text(
        state.get("service"),
        "unknown-service",
    )

    incident = _text(
        state.get("incident"),
        "SRE incident detected",
    )

    summary = (
        f"[Incident] {service}: {incident}"
    )

    description_sections = [
        "SRE Incident Response Platform Incident",
        f"Incident: {_text(state.get('incident'))}",
        f"Service: {_text(state.get('service'))}",
        (
            "Incident source: "
            f"{_text(state.get('incident_source'))}"
        ),
        (
            "AWS region: "
            f"{_text(state.get('aws_region'))}"
        ),
        (
            "CloudWatch alarm: "
            f"{_text(state.get('cloudwatch_alarm_name'))}"
        ),
        (
            "CloudWatch state: "
            f"{_text(state.get('cloudwatch_alarm_state'))}"
        ),
        (
            "CloudWatch metric: "
            f"{_text(state.get('cloudwatch_metric'))}"
        ),
        (
            "Metrics: "
            f"{_text(state.get('metrics'))}"
        ),
        (
            "Logs: "
            f"{_text(state.get('logs'))}"
        ),
        (
            "Infrastructure: "
            f"{_text(state.get('infrastructure'))}"
        ),
        (
            "Historical incidents: "
            f"{_text(state.get('historical_incidents'))}"
        ),
        (
            "Root cause: "
            f"{_text(state.get('root_cause'))}"
        ),
        (
            "Supporting evidence: "
            f"{_text(state.get('supporting_evidence'))}"
        ),
        (
            "Impact: "
            f"{_text(state.get('impact'))}"
        ),
        (
            "Recommendation: "
            f"{_text(state.get('recommendation'))}"
        ),
        (
            "Rollback plan: "
            f"{_text(state.get('rollback_plan'))}"
        ),
        (
            "Risk level: "
            f"{_text(state.get('risk_level'))}"
        ),
        (
            "Safety status: "
            f"{_text(state.get('safety_status'))}"
        ),
    ]

    description = {
        "type": "doc",
        "version": 1,
        "content": [
            _paragraph(section)
            for section in description_sections
        ],
    }

    return {
        "project": {
            "key": project_key,
        },
        "issuetype": {
            "id": issue_type_id,
        },
        "summary": summary,
        "description": description,
    }


def create_incident(
    state: IncidentState,
    client: JiraClient | None = None,
) -> dict[str, Any]:
    """Create a Jira Incident from IncidentState."""

    jira_client = client or JiraClient()

    fields = build_incident_fields(state)

    return jira_client.create_issue(fields)


def transition_incident_to_status(
    issue_key: str,
    status_name: str,
    client: JiraClient | None = None,
) -> None:
    """
    Transition an existing Jira incident to a
    requested destination status.
    """

    jira_client = client or JiraClient()

    jira_client.transition_issue_to_status(
        issue_key=issue_key,
        status_name=status_name,
    )