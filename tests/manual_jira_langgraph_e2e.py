from services import cloudwatch_incident_runner


def fake_detect_cloudwatch_incidents(
    region_name: str,
):
    return [
        {
            "incident": (
                "Test incident: order-api HTTP 500 "
                "errors detected."
            ),
            "service": "order-api",
            "incident_source": "Manual E2E Test",
            "aws_region": region_name,
            "cloudwatch_alarm_name": (
                "Manual-E2E-Test"
            ),
            "cloudwatch_alarm_state": "ALARM",
            "cloudwatch_metric": (
                "AWS/EC2/CPUUtilization"
            ),
            "metrics": (
                "Manual E2E test metrics."
            ),
            "impact": (
                "Test incident only. No production impact."
            ),
            "risk_level": "MEDIUM",
        }
    ]


cloudwatch_incident_runner.detect_cloudwatch_incidents = (
    fake_detect_cloudwatch_incidents
)


results = (
    cloudwatch_incident_runner
    .start_cloudwatch_incidents(
        region_name="us-east-1"
    )
)

print("\n========================================")
print("JIRA + LANGGRAPH E2E RESULT")
print("========================================")

for result in results:

    print("\nThread ID:")
    print(result["thread_id"])

    print("\nJira Issue:")
    print(
        result["incident"].get(
            "jira_issue_key"
        )
    )

    print("\nJira URL:")
    print(
        result["incident"].get(
            "jira_issue_url"
        )
    )

    print("\nJira Status:")
    print(
        result["incident"].get(
            "jira_status"
        )
    )

    print("\nGraph Result:")
    print(result["result"])