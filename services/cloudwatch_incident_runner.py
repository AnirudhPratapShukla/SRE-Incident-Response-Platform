from __future__ import annotations

import uuid
from typing import Any

from detection.cloudwatch_detector import (
    detect_cloudwatch_incidents,
)
from graph.workflow import incident_graph


def start_cloudwatch_incidents(
    region_name: str,
) -> list[dict[str, Any]]:
    """
    Detect active CloudWatch alarms and start the existing
    SRE LangGraph workflow for each detected incident.

    This function does not perform remediation itself.
    It only creates the incident state and starts the
    existing investigation workflow.
    """

    incidents = detect_cloudwatch_incidents(
        region_name=region_name
    )

    results: list[dict[str, Any]] = []

    for incident in incidents:

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

        print("\nIncident:")
        print(result["incident"])
