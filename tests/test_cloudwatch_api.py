from fastapi.testclient import TestClient

import api.main as api_main


def test_cloudwatch_endpoint_no_incidents():

    original_runner = (
        api_main.start_cloudwatch_incidents
    )

    try:

        api_main.start_cloudwatch_incidents = (
            lambda region_name: []
        )

        client = TestClient(api_main.app)

        response = client.post(
            "/cloudwatch/incidents",
            json={
                "region_name": "us-east-1"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "no_incidents"
        assert data["region"] == "us-east-1"
        assert data["incidents_detected"] == 0
        assert data["incidents"] == []

    finally:

        api_main.start_cloudwatch_incidents = (
            original_runner
        )


def test_cloudwatch_endpoint_with_incident():

    original_runner = (
        api_main.start_cloudwatch_incidents
    )

    try:

        api_main.start_cloudwatch_incidents = (
            lambda region_name: [
                {
                    "thread_id": "test-cloudwatch-thread",
                    "incident": {
                        "incident": "High CPU detected",
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
                    },
                    "result": {
                        "__interrupt__": [
                            type(
                                "Interrupt",
                                (),
                                {
                                    "value": (
                                        "Human approval required."
                                    )
                                }
                            )()
                        ]
                    }
                }
            ]
        )

        client = TestClient(api_main.app)

        response = client.post(
            "/cloudwatch/incidents",
            json={
                "region_name": "us-east-1"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "incidents_detected"
        assert data["region"] == "us-east-1"
        assert data["incidents_detected"] == 1
        assert len(data["incidents"]) == 1

        incident = data["incidents"][0]

        assert incident["thread_id"] == (
            "test-cloudwatch-thread"
        )

        assert incident["status"] == (
            "approval_required"
        )

        assert incident["approval_request"] == (
            "Human approval required."
        )

    finally:

        api_main.start_cloudwatch_incidents = (
            original_runner
        )


if __name__ == "__main__":

    print(
        "\nStarting CloudWatch API Tests...\n"
    )

    test_cloudwatch_endpoint_no_incidents()
    test_cloudwatch_endpoint_with_incident()

    print(
        "\nAll CloudWatch API tests passed."
    )
