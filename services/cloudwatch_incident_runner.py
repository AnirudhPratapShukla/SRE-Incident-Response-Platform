from __future__ import annotations

import os
import uuid
from typing import Any

from detection.cloudwatch_detector import (
    detect_cloudwatch_incidents,
)
from graph.workflow import incident_graph
from jira.incidents import create_incident


def _create_jira_incident(
    incident: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a Jira Incident and attach Jira metadata
    to the incident state.
    """

    jira_result = create_incident(incident)

    issue_key = jira_result.get("key")

    if not issue_key:
        raise RuntimeError(
            "Jira incident creation succeeded but "
            "no issue key was returned."
        )

    base_url = os.getenv(
        "JIRA_BASE_URL",
        "",
    ).rstrip("/")

    incident["jira_issue_key"] = issue_key

    if base_url:
        incident["jira_issue_url"] = (
            f"{base_url}/browse/{issue_key}"
        )

    incident["jira_status"] = "CREATED"

    return jira_result


def start_cloudwatch_incidents(
    region_name: str,
) -> list[dict[str, Any]]:
    """
    Detect active CloudWatch alarms, create a Jira
    Incident for each one, and start the existing
    SRE LangGraph workflow.

    Jira creation happens before the LangGraph workflow
    starts so every processed CloudWatch incident is
    recorded in Jira first.

    This function does not perform remediation itself.
    """

    incidents = detect_cloudwatch_incidents(
        region_name=region_name
    )

    results: list[dict[str, Any]] = []

    for incident in incidents:

        jira_result = _create_jira_incident(
            incident
        )

        thread_id = str(uuid.uuid4())

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        incident_graph.update_state(
            config,
            incident,
        )

        result = incident_graph.invoke(
            None,
            config=config,
        )

        results.append(
            {
                "thread_id": thread_id,
                "incident": incident,
                "jira": jira_result,
                "result": result,
            }
        )

    return results


if __name__ == "__main__":

    results = start_cloudwatch_incidents(
        region_name="us-east-1"
    )

    print(
        f"CloudWatch incidents started: "
        f"{len(results)}"
    )

    for result in results:

        print("\nThread ID:")
        print(result["thread_id"])

        print("\nJira:")
        print(
            result["incident"].get(
                "jira_issue_key"
            )
        )

        print("\nIncident:")
        print(result["incident"])