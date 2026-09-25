from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from tools.aws import (
    get_aws_region,
    get_cloudwatch_client,
    get_metric_statistics,
    list_cloudwatch_alarms,
    list_cloudwatch_metrics,
)


def test_get_aws_region_explicit_value():
    assert get_aws_region("ap-south-1") == "ap-south-1"


@patch.dict(
    "os.environ",
    {
        "AWS_REGION": "eu-west-1",
        "AWS_DEFAULT_REGION": "us-east-1",
    },
    clear=True,
)
def test_get_aws_region_from_environment():
    assert get_aws_region() == "eu-west-1"


@patch("tools.aws.boto3.Session")
def test_get_cloudwatch_client(mock_session):
    mock_session_instance = MagicMock()
    mock_session.return_value = mock_session_instance

    get_cloudwatch_client("us-east-1")

    mock_session.assert_called_once_with(
        region_name="us-east-1"
    )

    mock_session_instance.client.assert_called_once_with(
        "cloudwatch"
    )


@patch("tools.aws.get_cloudwatch_client")
def test_list_cloudwatch_metrics(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    paginator = MagicMock()

    paginator.paginate.return_value = [
        {
            "Metrics": [
                {
                    "Namespace": "AWS/EC2",
                    "MetricName": "CPUUtilization",
                    "Dimensions": [],
                },
                {
                    "Namespace": "AWS/EC2",
                    "MetricName": "NetworkIn",
                    "Dimensions": [],
                },
            ]
        }
    ]

    mock_client.get_paginator.return_value = paginator

    result = list_cloudwatch_metrics(
        namespace="AWS/EC2",
        max_items=1,
    )

    assert len(result) == 1
    assert result[0]["MetricName"] == "CPUUtilization"


@patch("tools.aws.get_cloudwatch_client")
def test_get_metric_statistics(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    mock_client.get_metric_statistics.return_value = {
        "Datapoints": [
            {
                "Timestamp": datetime(
                    2026,
                    9,
                    25,
                    12,
                    10,
                    tzinfo=timezone.utc,
                ),
                "Average": 75.5,
            }
        ]
    }

    result = get_metric_statistics(
        namespace="AWS/EC2",
        metric_name="CPUUtilization",
    )

    assert len(result) == 1
    assert result[0]["Average"] == 75.5

    mock_client.get_metric_statistics.assert_called_once()


@patch("tools.aws.get_cloudwatch_client")
def test_list_cloudwatch_alarms(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    paginator = MagicMock()

    paginator.paginate.return_value = [
        {
            "MetricAlarms": [
                {
                    "AlarmName": "HighCPU",
                    "StateValue": "ALARM",
                }
            ]
        }
    ]

    mock_client.get_paginator.return_value = paginator

    result = list_cloudwatch_alarms(
        state_value="ALARM"
    )

    assert len(result) == 1
    assert result[0]["AlarmName"] == "HighCPU"

    paginator.paginate.assert_called_once_with(
        StateValue="ALARM"
    )


def test_metric_statistics_rejects_naive_datetime():
    naive_datetime = datetime(2026, 9, 25, 12, 0)

    with pytest.raises(ValueError):
        get_metric_statistics(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            start_time=naive_datetime,
        )


def test_metric_statistics_rejects_invalid_period():
    with pytest.raises(ValueError):
        get_metric_statistics(
            namespace="AWS/EC2",
            metric_name="CPUUtilization",
            period=0,
        )
