from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import boto3


DEFAULT_REGION = "us-east-1"


def get_aws_region(region_name: str | None = None) -> str:
    """
    Resolve the AWS region using the following priority:

    1. Explicit function argument
    2. AWS_REGION environment variable
    3. AWS_DEFAULT_REGION environment variable
    4. Boto3 session configuration
    5. us-east-1 fallback
    """

    if region_name:
        return region_name

    env_region = (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
    )

    if env_region:
        return env_region

    session = boto3.Session()

    return session.region_name or DEFAULT_REGION


def get_cloudwatch_client(region_name: str | None = None):
    """
    Create a read-only CloudWatch client.

    Authentication is intentionally delegated to the standard
    Boto3/AWS credential chain. No access keys are stored here.
    """

    region = get_aws_region(region_name)

    session = boto3.Session(region_name=region)

    return session.client("cloudwatch")


def list_cloudwatch_metrics(
    namespace: str | None = None,
    metric_name: str | None = None,
    dimensions: Iterable[dict[str, str]] | None = None,
    region_name: str | None = None,
    max_items: int | None = None,
) -> list[dict[str, Any]]:
    """
    List CloudWatch metrics matching the supplied filters.

    This is a read-only operation.
    """

    client = get_cloudwatch_client(region_name)

    params: dict[str, Any] = {}

    if namespace:
        params["Namespace"] = namespace

    if metric_name:
        params["MetricName"] = metric_name

    if dimensions:
        params["Dimensions"] = list(dimensions)

    metrics: list[dict[str, Any]] = []

    paginator = client.get_paginator("list_metrics")

    for page in paginator.paginate(**params):
        page_metrics = page.get("Metrics", [])

        for metric in page_metrics:
            metrics.append(metric)

            if max_items is not None and len(metrics) >= max_items:
                return metrics[:max_items]

    return metrics


def get_metric_statistics(
    namespace: str,
    metric_name: str,
    dimensions: Iterable[dict[str, str]] | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    period: int = 300,
    statistics: Iterable[str] | None = None,
    region_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    Retrieve CloudWatch metric statistics for a time window.

    Defaults:
        - Last 15 minutes
        - 5-minute period
        - Average statistic

    This is a read-only operation.
    """

    if start_time is None:
        start_time = datetime.now(timezone.utc) - timedelta(minutes=15)

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    if start_time.tzinfo is None or end_time.tzinfo is None:
        raise ValueError(
            "start_time and end_time must be timezone-aware datetimes"
        )

    if period <= 0:
        raise ValueError("period must be greater than zero")

    requested_statistics = list(statistics or ["Average"])

    params: dict[str, Any] = {
        "Namespace": namespace,
        "MetricName": metric_name,
        "StartTime": start_time,
        "EndTime": end_time,
        "Period": period,
        "Statistics": requested_statistics,
    }

    if dimensions:
        params["Dimensions"] = list(dimensions)

    client = get_cloudwatch_client(region_name)

    response = client.get_metric_statistics(**params)

    datapoints = response.get("Datapoints", [])

    return sorted(
        datapoints,
        key=lambda item: item.get("Timestamp", datetime.min),
    )


def list_cloudwatch_alarms(
    state_value: str | None = None,
    region_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    List CloudWatch metric alarms.

    Optional state filtering can be used with values such as:

        OK
        ALARM
        INSUFFICIENT_DATA

    This is a read-only operation.
    """

    client = get_cloudwatch_client(region_name)

    params: dict[str, Any] = {}

    if state_value:
        params["StateValue"] = state_value

    alarms: list[dict[str, Any]] = []

    paginator = client.get_paginator("describe_alarms")

    for page in paginator.paginate(**params):
        alarms.extend(page.get("MetricAlarms", []))

    return alarms


if __name__ == "__main__":
    print("AWS CloudWatch integration")
    print(f"Region: {get_aws_region()}")

    metrics = list_cloudwatch_metrics(
        namespace="AWS/EC2",
        max_items=5,
    )

    print(f"EC2 metrics discovered: {len(metrics)}")

    alarms = list_cloudwatch_alarms()

    print(f"CloudWatch alarms discovered: {len(alarms)}")
