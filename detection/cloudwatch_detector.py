from __future__ import annotations

from typing import Any

from graph.state import IncidentState
from tools.aws import list_cloudwatch_alarms


def _get_dimension_value(
    alarm: dict[str, Any],
    dimension_name: str,
) -> str | None:
    """
    Extract a CloudWatch alarm dimension value.
    """

    for dimension in alarm.get("Dimensions", []):
        if dimension.get("Name") == dimension_name:
            return dimension.get("Value")

    return None


def alarm_to_incident_state(
    alarm: dict[str, Any],
    region_name: str,
) -> IncidentState:
    """
    Convert a CloudWatch alarm into the IncidentState
    format used by the SRE platform.
    """

    alarm_name = alarm.get(
        "AlarmName",
        "Unknown CloudWatch Alarm",
    )

    state_value = alarm.get(
        "StateValue",
        "UNKNOWN",
    )

    metric_name = alarm.get(
        "MetricName",
        "Unknown Metric",
    )

    namespace = alarm.get(
        "Namespace",
        "Unknown Namespace",
    )

    reason = alarm.get(
        "StateReason",
        "No state reason provided.",
    )

    instance_id = _get_dimension_value(
        alarm,
        "InstanceId",
    )

    service = (
        instance_id
        or alarm.get("AlarmDescription")
        or alarm_name
    )

    incident = (
        f"CloudWatch alarm '{alarm_name}' is in "
        f"{state_value} state. "
        f"Metric: {namespace}/{metric_name}. "
        f"Reason: {reason}"
    )

    metrics = (
        f"CloudWatch metric: {namespace}/{metric_name}; "
        f"Alarm state: {state_value}; "
        f"Threshold: {alarm.get('Threshold', 'N/A')}; "
        f"Comparison: "
        f"{alarm.get('ComparisonOperator', 'N/A')}"
    )

    return IncidentState(
        incident=incident,
        service=service,
        incident_source="AWS CloudWatch",
        aws_region=region_name,
        cloudwatch_alarm_name=alarm_name,
        cloudwatch_alarm_state=state_value,
        cloudwatch_metric=f"{namespace}/{metric_name}",
        metrics=metrics,
        impact=(
            f"CloudWatch detected an alarm condition for "
            f"{service}."
        ),
        risk_level="UNKNOWN",
    )


def detect_cloudwatch_incidents(
    region_name: str,
) -> list[IncidentState]:
    """
    Detect active CloudWatch incidents.

    Only alarms currently in ALARM state are converted
    into incidents.
    """

    alarms = list_cloudwatch_alarms(
        state_value="ALARM",
        region_name=region_name,
    )

    return [
        alarm_to_incident_state(
            alarm=alarm,
            region_name=region_name,
        )
        for alarm in alarms
    ]


if __name__ == "__main__":

    region = "us-east-1"

    incidents = detect_cloudwatch_incidents(
        region_name=region
    )

    print(
        f"CloudWatch incidents detected: "
        f"{len(incidents)}"
    )

    for incident in incidents:
        print("\nIncident:")
        print(incident)
