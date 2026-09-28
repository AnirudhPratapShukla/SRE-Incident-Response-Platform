from unittest.mock import patch

from detection.cloudwatch_detector import (
    alarm_to_incident_state,
    detect_cloudwatch_incidents,
)


def sample_alarm():
    return {
        "AlarmName": "HighCPU-order-api",
        "AlarmDescription": "order-api EC2 instance",
        "StateValue": "ALARM",
        "StateReason": "Threshold Crossed",
        "Namespace": "AWS/EC2",
        "MetricName": "CPUUtilization",
        "Threshold": 80.0,
        "ComparisonOperator": "GreaterThanThreshold",
        "Dimensions": [
            {
                "Name": "InstanceId",
                "Value": "i-0123456789abcdef0",
            }
        ],
    }


def test_alarm_to_incident_state():
    result = alarm_to_incident_state(
        alarm=sample_alarm(),
        region_name="us-east-1",
    )

    assert result["incident_source"] == "AWS CloudWatch"
    assert result["aws_region"] == "us-east-1"
    assert result["cloudwatch_alarm_name"] == "HighCPU-order-api"
    assert result["cloudwatch_alarm_state"] == "ALARM"
    assert result["cloudwatch_metric"] == "AWS/EC2/CPUUtilization"
    assert result["service"] == "i-0123456789abcdef0"
    assert "Threshold Crossed" in result["incident"]
    assert "CPUUtilization" in result["metrics"]


@patch("detection.cloudwatch_detector.list_cloudwatch_alarms")
def test_detect_cloudwatch_incidents(mock_list_alarms):
    mock_list_alarms.return_value = [
        sample_alarm()
    ]

    incidents = detect_cloudwatch_incidents(
        region_name="us-east-1"
    )

    assert len(incidents) == 1

    incident = incidents[0]

    assert incident["cloudwatch_alarm_name"] == "HighCPU-order-api"

    mock_list_alarms.assert_called_once_with(
        state_value="ALARM",
        region_name="us-east-1",
    )


@patch("detection.cloudwatch_detector.list_cloudwatch_alarms")
def test_detect_cloudwatch_incidents_when_no_alarms(
    mock_list_alarms,
):
    mock_list_alarms.return_value = []

    incidents = detect_cloudwatch_incidents(
        region_name="us-east-1"
    )

    assert incidents == []
