from __future__ import annotations

import os
import uuid
from typing import Any

from detection.cloudwatch_detector import (
    detect_cloudwatch_incidents,
)
from graph.workflow import incident_graph
from jira.incidents import create_incident
from jira.lifecycle import mark_in_progress


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


def _mark_jira_in_progress(
    incident: dict[str, Any],
) -> None:
    """
    Move the Jira incident to In Progress.

    The Jira issue key must already exist in the
    incident state.
    """

    issue_key = incident.get(
        "jira_issue_key"
    )

    if not issue_key:
        raise RuntimeError(
            "Cannot move Jira incident to In Progress "
            "because jira_issue_key is missing."
        )

    mark_in_progress(
        issue_key=issue_key
    )

    incident["jira_status"] = "IN PROGRESS"


def start_cloudwatch_incidents(
    region_name: str,
) -> list[dict[str, Any]]:
    """
    Detect active CloudWatch alarms, create a Jira
    Incident for each one, move the Jira incident to
    In Progress, and start the existing SRE LangGraph
    workflow.

    Jira creation happens before the LangGraph workflow
    starts so every processed CloudWatch incident is
    recorded in Jira first.

    Jira is moved to In Progress immediately before
    investigation begins.

    The final persisted LangGraph state is returned so
    Jira lifecycle updates such as IN REVIEW are reflected
    in the returned incident data.

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

        _mark_jira_in_progress(
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

        # Read the latest persisted state.
        # This is important because the graph may have
        # updated jira_status to IN REVIEW before the
        # human approval interrupt.
        current_state = incident_graph.get_state(
            config
        ).values

        results.append(
            {
                "thread_id": thread_id,
                "incident": current_state,
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

        print("\nJira Status:")
        print(
            result["incident"].get(
                "jira_status"
            )
        )

        print("\nIncident:")
        print(result["incident"])