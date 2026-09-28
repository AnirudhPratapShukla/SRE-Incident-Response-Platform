import os
from typing import Any

from dotenv import load_dotenv

from jira.client import JiraClient
from graph.state import IncidentState


def _text(value: Any, default: str = "Not available") -> str:
    """Convert a value to clean text."""

    if value is None:
        return default

    value = str(value).strip()

    return value if value else default


def _paragraph(text: str) -> dict[str, Any]:
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

    project_key = os.getenv("JIRA_PROJECT_KEY")
    issue_type_id = os.getenv("JIRA_INCIDENT_ISSUE_TYPE_ID")

    if not project_key:
        raise ValueError(
            "JIRA_PROJECT_KEY is not configured."
        )

    if not issue_type_id:
        raise ValueError(
            "JIRA_INCIDENT_ISSUE_TYPE_ID is not configured."
        )

    service = _text(state.get("service"), "unknown-service")
    incident = _text(
        state.get("incident"),
        "SRE incident detected",
    )

    summary = f"[Incident] {service}: {incident}"

    description_sections = [
        "SRE Incident Response Platform Incident",
        f"Incident: {_text(state.get('incident'))}",
        f"Service: {_text(state.get('service'))}",
        f"Incident source: {_text(state.get('incident_source'))}",
        f"AWS region: {_text(state.get('aws_region'))}",
        f"CloudWatch alarm: {_text(state.get('cloudwatch_alarm_name'))}",
        f"CloudWatch state: {_text(state.get('cloudwatch_alarm_state'))}",
        f"CloudWatch metric: {_text(state.get('cloudwatch_metric'))}",
        f"Metrics: {_text(state.get('metrics'))}",
        f"Logs: {_text(state.get('logs'))}",
        f"Infrastructure: {_text(state.get('infrastructure'))}",
        f"Historical incidents: {_text(state.get('historical_incidents'))}",
        f"Root cause: {_text(state.get('root_cause'))}",
        f"Supporting evidence: {_text(state.get('supporting_evidence'))}",
        f"Impact: {_text(state.get('impact'))}",
        f"Recommendation: {_text(state.get('recommendation'))}",
        f"Rollback plan: {_text(state.get('rollback_plan'))}",
        f"Risk level: {_text(state.get('risk_level'))}",
        f"Safety status: {_text(state.get('safety_status'))}",
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